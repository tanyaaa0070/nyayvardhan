"""
NyayVandan - FastAPI Backend Application
==========================================
Main REST API server for the Judicial Decision Support System.

Endpoints:
  POST /api/analyze    — Full case analysis pipeline
  GET  /api/health     — Health check
  GET  /api/stats      — Dataset statistics

"NyayVandan assists judicial reasoning by retrieving, explaining, and
 ethically evaluating similar legal precedents using offline AI models—
 without predicting outcomes or replacing human judgment."

⚠️ ALL processing is LOCAL. No external APIs are called.
"""

import os
import sys
import traceback

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- Add project root to path ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import (
    JUDGMENTS_CSV,
    UNIFIED_CSV,
    CIVILSUM_LIMIT,
    DEFAULT_TOP_K,
    MAX_TOP_K,
    HOST,
    PORT,
    FAISS_INDEX_PATH,
    EMBEDDINGS_NPY,
)
from backend.preprocessor import preprocess_case
from backend.ner import extract_entities
from backend.embeddings import EmbeddingEngine
from backend.retriever import CaseRetriever
from backend.explainability import explain_similarity
from backend.ethics import run_ethical_review
from backend.data_loader import load_unified_dataset

# ===================== App Setup =====================

app = FastAPI(
    title="NyayVandan API",
    description=(
        "Judicial Decision Support System — retrieves, explains, and ethically "
        "evaluates similar legal precedents. Advisory only; never replaces "
        "judicial discretion."
    ),
    version="2.0.0",
)

# CORS: Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Global State =====================

# These are initialized on startup
df_cases: pd.DataFrame = None
embedding_engine: EmbeddingEngine = None
case_retriever: CaseRetriever = None
constitution_lookup: dict = {}  # Article number → text (from Constitution dataset)

# ===================== Request / Response Models =====================

class AnalyzeRequest(BaseModel):
    """Request body for case analysis."""
    case_text: str = Field(
        ...,
        min_length=20,
        description="Raw case facts to analyze. Minimum 20 characters."
    )
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        le=MAX_TOP_K,
        description=f"Number of similar cases to retrieve (1-{MAX_TOP_K})"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    dataset_loaded: bool
    index_ready: bool
    total_cases: int


# ===================== Startup Event =====================

@app.on_event("startup")
async def startup_event():
    """
    Initialize all components on server startup:
      1. Load & merge ALL Kaggle datasets via unified loader
      2. Initialize Sentence-BERT embedding engine
      3. Build FAISS index (force rebuild for new data)
      4. Initialize hybrid retriever
    """
    global df_cases, embedding_engine, case_retriever, constitution_lookup
    
    print("=" * 60)
    print("  NyayVandan — Judicial Decision Support System")
    print("  Starting backend initialization...")
    print("=" * 60)
    
    # 1. Load ALL datasets via unified loader
    #    This merges: sample judgments + CivilSum + IPC QA + CrPC QA + Constitution QA
    df_cases, constitution_lookup = load_unified_dataset(
        civilsum_limit=CIVILSUM_LIMIT
    )
    
    # Fill NaN values with empty strings for text fields
    text_cols = ["case_text", "ipc_sections", "crpc_sections", 
                 "constitutional_articles", "case_title", "judgment_outcome"]
    for col in text_cols:
        if col in df_cases.columns:
            df_cases[col] = df_cases[col].fillna("")
    
    print(f"Loaded {len(df_cases)} total records from all datasets")
    if constitution_lookup:
        print(f"Constitution enrichment: {len(constitution_lookup)} articles loaded")
    
    # 2. Initialize embedding engine
    embedding_engine = EmbeddingEngine()
    
    # 3. Force rebuild FAISS index with the new unified data
    #    (delete old index so it rebuilds with all datasets)
    if os.path.exists(FAISS_INDEX_PATH):
        os.remove(FAISS_INDEX_PATH)
    if os.path.exists(EMBEDDINGS_NPY):
        os.remove(EMBEDDINGS_NPY)
    
    embedding_engine.load_index(df_cases)
    
    # 4. Initialize hybrid retriever
    case_retriever = CaseRetriever(embedding_engine, df_cases)
    
    print("=" * 60)
    print("  NyayVandan Backend READY")
    print(f"  {len(df_cases)} records indexed from all datasets")
    print(f"  Listening on {HOST}:{PORT}")
    print("=" * 60)


# ===================== API Endpoints =====================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if df_cases is not None else "initializing",
        dataset_loaded=df_cases is not None,
        index_ready=embedding_engine is not None and embedding_engine.index is not None,
        total_cases=len(df_cases) if df_cases is not None else 0
    )


@app.get("/api/stats")
async def get_stats():
    """Return dataset statistics."""
    if df_cases is None:
        raise HTTPException(status_code=503, detail="System not initialized yet")
    
    return {
        "total_cases": len(df_cases),
        "courts": df_cases["court"].value_counts().to_dict() if "court" in df_cases.columns else {},
        "year_range": {
            "min": int(df_cases["year"].min()) if "year" in df_cases.columns else 0,
            "max": int(df_cases["year"].max()) if "year" in df_cases.columns else 0,
        },
        "outcomes": df_cases["judgment_outcome"].value_counts().to_dict() if "judgment_outcome" in df_cases.columns else {},
        "sources": df_cases["source"].value_counts().to_dict() if "source" in df_cases.columns else {},
        "constitution_articles_loaded": len(constitution_lookup),
    }


@app.post("/api/analyze")
async def analyze_case(request: AnalyzeRequest):
    """
    Full NyayVandan analysis pipeline.
    
    Pipeline Steps:
      1. Preprocess input text
      2. Extract legal entities (IPC, CrPC, Articles)
      3. Retrieve Top-K similar cases (hybrid semantic + lexical + entity)
      4. Generate explainability for each match
      5. Run ethical / bias review
      6. Return structured, citeable JSON response
    
    ⚠️ This endpoint is ADVISORY ONLY.
       It does NOT predict outcomes or automate judicial decisions.
    """
    if case_retriever is None:
        raise HTTPException(status_code=503, detail="System not initialized. Please wait.")
    
    try:
        # --- Stage 1: Preprocess ---
        preprocessed = preprocess_case(request.case_text)
        
        # --- Stage 2: Legal Entity Extraction ---
        extracted_entities = extract_entities(request.case_text)
        
        # --- Stage 3 & 4: Hybrid Retrieval (Semantic + Lexical + Entity) ---
        similar_cases = case_retriever.retrieve(
            query_text=request.case_text,
            top_k=request.top_k
        )
        
        # --- Stage 5: Explainability ---
        explanations = []
        for case in similar_cases:
            explanation = explain_similarity(
                query_text=request.case_text,
                query_entities=extracted_entities,
                case_data=case
            )
            explanations.append(explanation)
        
        # --- Stage 6: Ethical Review ---
        ethical_flags = run_ethical_review(similar_cases, extracted_entities)
        
        # --- Stage 7: Structured Output ---
        return {
            "status": "success",
            "query_info": {
                "original_length": len(request.case_text),
                "cleaned_length": len(preprocessed["cleaned"]),
                "token_count": preprocessed["token_count"],
                "top_k_requested": request.top_k,
            },
            "extracted_entities": extracted_entities,
            "similar_cases": [
                {
                    "case_id": c["case_id"],
                    "case_title": c["case_title"],
                    "court": c["court"],
                    "year": c["year"],
                    "case_text": c["case_text"],
                    "ipc_sections": c["ipc_sections"],
                    "crpc_sections": c["crpc_sections"],
                    "constitutional_articles": c["constitutional_articles"],
                    "judgment_outcome": c["judgment_outcome"],
                    "similarity_label": c["similarity_label"],
                    "scores": c["scores"],
                }
                for c in similar_cases
            ],
            "explanations": explanations,
            "ethical_flags": ethical_flags,
            "disclaimer": (
                "NyayVandan is an advisory system. All outputs are for judicial "
                "reference only. This system does not predict outcomes, assign "
                "probabilities, or automate any judicial decision. Judicial "
                "discretion remains paramount."
            ),
        }
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )


# ===================== Run Server =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )
