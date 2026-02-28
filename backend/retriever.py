"""
NyayVandan - Case Retrieval Engine
=====================================
Pipeline Stage 4: Case-Based Reasoning (CBR)

Retrieves Top-K similar cases using a hybrid approach:
  1. Semantic similarity (Sentence-BERT + FAISS)
  2. Lexical overlap (TF-IDF cosine similarity)
  3. Legal entity overlap (IPC/CrPC/Article matching)

The final ranking is a weighted combination of all three signals.

⚠️ This module RETRIEVES precedents — it does NOT predict outcomes.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.embeddings import EmbeddingEngine
from backend.ner import extract_entities, extract_sections_from_csv_field
from backend.preprocessor import clean_text


class CaseRetriever:
    """
    Hybrid case retrieval engine combining semantic, lexical, and entity-based signals.
    
    Weights:
      - Semantic (SBERT + FAISS): 0.50
      - Lexical (TF-IDF): 0.30
      - Entity overlap: 0.20
    """
    
    # Hybrid ranking weights
    W_SEMANTIC = 0.50
    W_LEXICAL = 0.30
    W_ENTITY = 0.20
    
    def __init__(self, embedding_engine: EmbeddingEngine, df: pd.DataFrame):
        """
        Initialize the retriever.
        
        Args:
            embedding_engine: Initialized EmbeddingEngine with loaded FAISS index
            df: DataFrame of all cases in the dataset
        """
        self.engine = embedding_engine
        self.df = df.copy()
        
        # Build TF-IDF matrix for lexical similarity
        # Using unigrams only and limited features to stay memory-efficient
        self.tfidf = TfidfVectorizer(
            max_features=3000,
            stop_words="english",
            ngram_range=(1, 1),
            sublinear_tf=True,
            dtype=np.float32
        )
        
        # Clean texts for TF-IDF
        cleaned_texts = [clean_text(str(t))[:2000] for t in self.df["case_text"].tolist()]
        self.tfidf_matrix = self.tfidf.fit_transform(cleaned_texts)
        
        print(f"TF-IDF matrix built: {self.tfidf_matrix.shape}")
    
    def _compute_entity_overlap(self, query_entities: dict, case_row: pd.Series) -> float:
        """
        Compute Jaccard-like overlap between query entities and a case's legal references.
        
        Args:
            query_entities: Extracted entities from query
            case_row: A row from the cases DataFrame
        
        Returns:
            Float overlap score in [0, 1]
        """
        # Gather query entity sets
        q_ipc = set(query_entities.get("IPC_Sections", []))
        q_crpc = set(query_entities.get("CrPC_Sections", []))
        q_articles = set(query_entities.get("Constitutional_Articles", []))
        
        # Gather case entity sets from CSV fields
        c_ipc = set(extract_sections_from_csv_field(
            str(case_row.get("ipc_sections", "")), "IPC"
        ))
        c_crpc = set(extract_sections_from_csv_field(
            str(case_row.get("crpc_sections", "")), "CrPC"
        ))
        c_articles = set(extract_sections_from_csv_field(
            str(case_row.get("constitutional_articles", "")), "Article"
        ))
        
        # Compute overlap for each category
        all_query = q_ipc | q_crpc | q_articles
        all_case = c_ipc | c_crpc | c_articles
        
        if not all_query and not all_case:
            return 0.0
        
        union = all_query | all_case
        if len(union) == 0:
            return 0.0
        
        intersection = all_query & all_case
        return len(intersection) / len(union)
    
    def _compute_lexical_similarity(self, query_text: str, case_indices: list) -> dict:
        """
        Compute TF-IDF cosine similarity between query and candidate cases.
        
        Args:
            query_text: Cleaned query text
            case_indices: List of candidate case indices in the DataFrame
        
        Returns:
            Dict mapping index → similarity score
        """
        query_vec = self.tfidf.transform([clean_text(query_text)])
        
        scores = {}
        for idx in case_indices:
            if idx < self.tfidf_matrix.shape[0]:
                sim = cosine_similarity(query_vec, self.tfidf_matrix[idx:idx+1])[0][0]
                scores[idx] = float(sim)
        
        return scores
    
    def retrieve(self, query_text: str, top_k: int = 5) -> list:
        """
        Retrieve Top-K similar cases using hybrid ranking.
        
        Pipeline:
          1. Use FAISS for initial semantic retrieval (2x top_k candidates)
          2. Compute TF-IDF lexical scores for candidates
          3. Compute entity overlap scores for candidates
          4. Combine with weighted sum → final ranking
          5. Return top_k results
        
        Args:
            query_text: Raw case facts
            top_k: Number of results to return
        
        Returns:
            List of dicts with case info and scores
        """
        # Step 1: Semantic retrieval — get 2x candidates for re-ranking
        candidate_count = min(top_k * 2, len(self.df))
        semantic_results = self.engine.search(query_text, top_k=candidate_count)
        
        # Extract query entities for overlap scoring
        query_entities = extract_entities(query_text)
        
        # Map case_id → DataFrame index
        case_id_to_idx = {cid: i for i, cid in enumerate(self.df["case_id"].tolist())}
        
        # Step 2–3: Score all candidates
        candidate_indices = []
        for r in semantic_results:
            idx = case_id_to_idx.get(r["case_id"])
            if idx is not None:
                candidate_indices.append(idx)
        
        lexical_scores = self._compute_lexical_similarity(query_text, candidate_indices)
        
        scored_results = []
        for r in semantic_results:
            idx = case_id_to_idx.get(r["case_id"])
            if idx is None:
                continue
            
            case_row = self.df.iloc[idx]
            
            # Individual scores
            sem_score = r["similarity_score"]
            lex_score = lexical_scores.get(idx, 0.0)
            ent_score = self._compute_entity_overlap(query_entities, case_row)
            
            # Weighted hybrid score
            hybrid_score = (
                self.W_SEMANTIC * sem_score +
                self.W_LEXICAL * lex_score +
                self.W_ENTITY * ent_score
            )
            
            # Descriptive similarity label based on hybrid score
            if hybrid_score >= 0.6:
                similarity_label = "Highly Similar"
            elif hybrid_score >= 0.4:
                similarity_label = "Moderately Similar"
            elif hybrid_score >= 0.25:
                similarity_label = "Somewhat Similar"
            else:
                similarity_label = "Low Similarity"
            
            scored_results.append({
                "case_id": r["case_id"],
                "case_title": case_row.get("case_title", ""),
                "court": case_row.get("court", ""),
                "year": int(case_row.get("year", 0)),
                "case_text": case_row.get("case_text", ""),
                "ipc_sections": str(case_row.get("ipc_sections", "")),
                "crpc_sections": str(case_row.get("crpc_sections", "")),
                "constitutional_articles": str(case_row.get("constitutional_articles", "")),
                "judgment_outcome": case_row.get("judgment_outcome", ""),
                "scores": {
                    "semantic": round(sem_score, 4),
                    "lexical": round(lex_score, 4),
                    "entity_overlap": round(ent_score, 4),
                    "hybrid": round(hybrid_score, 4)
                },
                "similarity_label": similarity_label
            })
        
        # Step 5: Sort by hybrid score, return top_k
        scored_results.sort(key=lambda x: x["scores"]["hybrid"], reverse=True)
        return scored_results[:top_k]
