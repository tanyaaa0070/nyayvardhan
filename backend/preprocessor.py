"""
NyayVandan - Text Preprocessor
================================
Cleans, normalizes, and tokenizes raw legal case text.
Pipeline Stage 1: Case Input Processing.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Clean raw legal text for downstream NLP processing.
    
    Steps:
      1. Lowercase normalization
      2. Remove extra whitespace and line breaks
      3. Remove special characters (keep legal-relevant punctuation)
      4. Normalize section references
      5. Remove noise patterns common in court documents
    
    Args:
        text: Raw case facts text
    Returns:
        Cleaned text string
    """
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Normalize whitespace: replace newlines, tabs, multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # 3. Remove URLs (sometimes found in digital court records)
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # 4. Normalize common legal abbreviations for consistency
    #    e.g., "i.p.c" → "ipc", "cr.p.c" → "crpc"
    text = re.sub(r'i\.p\.c\.?', 'ipc', text)
    text = re.sub(r'cr\.p\.c\.?', 'crpc', text)
    text = re.sub(r'c\.p\.c\.?', 'cpc', text)
    
    # 5. Remove case numbering noise (e.g., "para 12.", "page no. 5")
    text = re.sub(r'\bpara\s*\.?\s*\d+\s*\.?', '', text)
    text = re.sub(r'\bpage\s*no\s*\.?\s*\d+', '', text)
    
    # 6. Remove excessive punctuation but keep periods, commas, hyphens
    text = re.sub(r'[^\w\s.,;:\-/()]', '', text)
    
    # 7. Final whitespace cleanup
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text


def tokenize(text: str) -> list:
    """
    Simple whitespace tokenizer for cleaned legal text.
    
    Args:
        text: Cleaned text string
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    # Split on whitespace; remove empty and single-character tokens
    tokens = text.split()
    tokens = [t for t in tokens if len(t) > 1]
    return tokens


def preprocess_case(raw_text: str) -> dict:
    """
    Full preprocessing pipeline for a case input.
    
    Returns:
        dict with 'original', 'cleaned', and 'tokens' keys
    """
    cleaned = clean_text(raw_text)
    tokens = tokenize(cleaned)
    return {
        "original": raw_text,
        "cleaned": cleaned,
        "tokens": tokens,
        "token_count": len(tokens)
    }
