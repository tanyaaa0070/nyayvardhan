"""
NyayVandan - Embedding Engine
================================
Pipeline Stage 3: Semantic Embedding

Generates sentence embeddings using local Sentence-BERT model.
Builds and manages FAISS index for efficient similarity search.

⚠️ ALL models run LOCALLY. No API calls.
"""

import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

from backend.config import (
    SBERT_MODEL_NAME,
    JUDGMENTS_CSV,
    FAISS_INDEX_PATH,
    EMBEDDINGS_NPY,
)


class EmbeddingEngine:
    """
    Manages sentence embeddings and FAISS similarity index.
    
    Responsibilities:
      - Load/download Sentence-BERT model (cached locally)
      - Encode text into dense vectors
      - Build FAISS index from dataset
      - Save/load FAISS index to/from disk
    """
    
    def __init__(self):
        """Initialize the embedding engine with local Sentence-BERT model."""
        print(f"📦 Loading Sentence-BERT model: {SBERT_MODEL_NAME}")
        self.model = SentenceTransformer(SBERT_MODEL_NAME)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.embeddings = None
        self.case_ids = []
        print(f"✅ Model loaded. Embedding dimension: {self.dimension}")
    
    def encode(self, texts: list, batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        Encode a list of texts into dense embeddings.
        
        Args:
            texts: List of text strings to encode
            batch_size: Encoding batch size
            show_progress: Whether to show progress bar
        
        Returns:
            numpy array of shape (len(texts), dimension)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2-normalize for cosine similarity via inner product
        )
        return embeddings
    
    def build_index(self, df: pd.DataFrame, text_column: str = "case_text"):
        """
        Build FAISS index from a DataFrame of cases.
        
        Uses IndexFlatIP (inner product) on L2-normalized vectors,
        which is equivalent to cosine similarity.
        
        Args:
            df: DataFrame containing case data
            text_column: Column name containing case text
        """
        texts = df[text_column].tolist()
        self.case_ids = df["case_id"].tolist()
        
        print(f"🔄 Encoding {len(texts)} cases...")
        self.embeddings = self.encode(texts, show_progress=True)
        
        # Build FAISS index using inner product (cosine sim on normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(self.embeddings.astype(np.float32))
        
        print(f"✅ FAISS index built with {self.index.ntotal} vectors")
    
    def save_index(self):
        """Persist FAISS index and embeddings to disk."""
        if self.index is not None:
            faiss.write_index(self.index, FAISS_INDEX_PATH)
            np.save(EMBEDDINGS_NPY, self.embeddings)
            print(f"💾 Index saved to {FAISS_INDEX_PATH}")
            print(f"💾 Embeddings saved to {EMBEDDINGS_NPY}")
    
    def load_index(self, df: pd.DataFrame):
        """
        Load FAISS index from disk if available, otherwise build from scratch.
        
        Args:
            df: DataFrame of cases (needed for case_ids mapping)
        """
        self.case_ids = df["case_id"].tolist()
        
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(EMBEDDINGS_NPY):
            print("📂 Loading pre-built FAISS index from disk...")
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            self.embeddings = np.load(EMBEDDINGS_NPY)
            print(f"✅ Loaded index with {self.index.ntotal} vectors")
        else:
            print("⚠️ No pre-built index found. Building from dataset...")
            self.build_index(df)
            self.save_index()
    
    def search(self, query_text: str, top_k: int = 5) -> list:
        """
        Search for the most similar cases to a query text.
        
        Args:
            query_text: The input case facts to search against
            top_k: Number of similar cases to retrieve
        
        Returns:
            List of tuples: (case_id, similarity_score, index_position)
        """
        if self.index is None:
            raise ValueError("FAISS index not initialized. Call load_index() first.")
        
        # Encode the query
        query_embedding = self.encode([query_text])
        
        # Search FAISS index
        scores, indices = self.index.search(
            query_embedding.astype(np.float32), 
            min(top_k, self.index.ntotal)
        )
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.case_ids):
                results.append({
                    "case_id": self.case_ids[idx],
                    "similarity_score": float(score),
                    "index_position": int(idx)
                })
        
        return results
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get the embedding vector for a single text."""
        return self.encode([text])[0]
