"""
NyayVandan - Configuration Module
===================================
Centralized configuration for all backend components.
All paths are local; no external API endpoints.
"""

import os

# --- Paths (relative to project root) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Dataset file paths
JUDGMENTS_CSV = os.path.join(DATA_DIR, "judgments.csv")
UNIFIED_CSV = os.path.join(DATA_DIR, "unified_judgments.csv")

# How many CivilSum cases to include (controls total dataset size)
CIVILSUM_LIMIT = 500

# FAISS index persistence path
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "embeddings.faiss")

# Cached embeddings (numpy array)
EMBEDDINGS_NPY = os.path.join(DATA_DIR, "embeddings.npy")

# --- Model Configuration  (ALL LOCAL, NO APIs) ---
# Sentence-BERT model for semantic embeddings
# This model is downloaded once and cached locally
SBERT_MODEL_NAME = "all-MiniLM-L6-v2"

# spaCy model for NER
SPACY_MODEL = "en_core_web_sm"

# --- Retrieval Settings ---
DEFAULT_TOP_K = 5          # Default number of similar cases to retrieve
MAX_TOP_K = 15             # Maximum allowed Top-K

# --- Explainability Settings ---
LIME_NUM_FEATURES = 10     # Number of features for LIME explanation
LIME_NUM_SAMPLES = 100     # Number of perturbation samples for LIME

# --- Ethical Review Thresholds ---
# If precedent diversity score falls below this, raise a flag
DIVERSITY_THRESHOLD = 0.3
# Minimum number of distinct courts for a balanced result set
MIN_COURT_DIVERSITY = 2
# Minimum year range to avoid temporal bias
MIN_YEAR_RANGE = 2

# --- Server Settings ---
HOST = "0.0.0.0"
PORT = 8000
