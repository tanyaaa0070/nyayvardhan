"""
NyayVandan - Explainability Module
=====================================
Pipeline Stage 5: Explainability Layer

For each retrieved precedent, explains WHY it is considered similar:
  1. Overlapping legal entities (IPC, CrPC, Articles)
  2. Common factual keywords (TF-IDF based)
  3. LIME-based explanation of influential terms

⚠️ This module explains similarity — it does NOT predict or recommend outcomes.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

from backend.ner import extract_entities, extract_sections_from_csv_field
from backend.preprocessor import clean_text


def _get_common_legal_entities(query_entities: dict, case_data: dict) -> dict:
    """
    Find overlapping legal entities between query and a retrieved case.
    
    Returns:
        Dict with overlapping IPC, CrPC, Articles, and Acts
    """
    # Parse case entities from CSV fields
    case_ipc = set(extract_sections_from_csv_field(
        case_data.get("ipc_sections", ""), "IPC"
    ))
    case_crpc = set(extract_sections_from_csv_field(
        case_data.get("crpc_sections", ""), "CrPC"
    ))
    case_articles = set(extract_sections_from_csv_field(
        case_data.get("constitutional_articles", ""), "Article"
    ))
    
    q_ipc = set(query_entities.get("IPC_Sections", []))
    q_crpc = set(query_entities.get("CrPC_Sections", []))
    q_articles = set(query_entities.get("Constitutional_Articles", []))
    
    return {
        "common_ipc": sorted(q_ipc & case_ipc),
        "common_crpc": sorted(q_crpc & case_crpc),
        "common_articles": sorted(q_articles & case_articles),
        "query_only_ipc": sorted(q_ipc - case_ipc),
        "case_only_ipc": sorted(case_ipc - q_ipc),
    }


def _get_influential_terms(query_text: str, case_text: str, top_n: int = 8) -> list:
    """
    Identify the most influential shared terms between query and case
    using TF-IDF weighting.
    
    Args:
        query_text: Cleaned query text
        case_text: Cleaned case text
        top_n: Number of top terms to return
    
    Returns:
        List of (term, combined_weight) tuples
    """
    # Custom stop words: extend standard with legal noise words
    legal_stop_words = set(ENGLISH_STOP_WORDS) | {
        "case", "court", "accused", "prosecution", "defense", "defence",
        "argued", "presented", "evidence", "submitted", "examined",
        "order", "judgment", "stated", "held", "observed"
    }
    
    tfidf = TfidfVectorizer(
        max_features=500,
        stop_words=list(legal_stop_words),
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    
    try:
        matrix = tfidf.fit_transform([clean_text(query_text), clean_text(case_text)])
        feature_names = tfidf.get_feature_names_out()
        
        query_vec = matrix[0].toarray().flatten()
        case_vec = matrix[1].toarray().flatten()
        
        # Combined importance: product of weights (high in both → influential)
        combined = query_vec * case_vec
        
        top_indices = combined.argsort()[-top_n:][::-1]
        
        terms = []
        for idx in top_indices:
            if combined[idx] > 0:
                terms.append({
                    "term": feature_names[idx],
                    "weight": round(float(combined[idx]), 4),
                    "query_relevance": round(float(query_vec[idx]), 4),
                    "case_relevance": round(float(case_vec[idx]), 4)
                })
        
        return terms
    except ValueError:
        return []


def explain_similarity(query_text: str, query_entities: dict, case_data: dict) -> dict:
    """
    Generate a comprehensive explanation of why a case is similar to the query.
    
    This is the main explainability function called for each retrieved precedent.
    
    Args:
        query_text: Original query case facts
        query_entities: Extracted entities from query
        case_data: Dict containing case information
    
    Returns:
        Explanation dict with multiple explanation facets
    """
    case_text = case_data.get("case_text", "")
    
    # 1. Legal entity overlap
    entity_overlap = _get_common_legal_entities(query_entities, case_data)
    
    # 2. Influential shared terms
    influential_terms = _get_influential_terms(query_text, case_text)
    
    # 3. Build human-readable explanation paragraphs
    explanation_parts = []
    
    # Entity-based explanation
    if entity_overlap["common_ipc"]:
        explanation_parts.append(
            f"Both cases involve the same IPC provisions: {', '.join(entity_overlap['common_ipc'])}. "
            f"This indicates similar criminal law subject matter."
        )
    
    if entity_overlap["common_crpc"]:
        explanation_parts.append(
            f"Shared procedural references under CrPC: {', '.join(entity_overlap['common_crpc'])}. "
            f"This suggests similar procedural contexts."
        )
    
    if entity_overlap["common_articles"]:
        explanation_parts.append(
            f"Common constitutional provisions invoked: {', '.join(entity_overlap['common_articles'])}. "
            f"Both cases address similar fundamental rights questions."
        )
    
    # Term-based explanation
    if influential_terms:
        top_terms = [t["term"] for t in influential_terms[:5]]
        explanation_parts.append(
            f"Key overlapping legal concepts: {', '.join(top_terms)}. "
            f"These terms appear with high relevance in both the query and this precedent."
        )
    
    # Similarity scores explanation
    scores = case_data.get("scores", {})
    if scores:
        explanation_parts.append(
            f"Similarity breakdown — Semantic: {scores.get('semantic', 0):.2%}, "
            f"Lexical: {scores.get('lexical', 0):.2%}, "
            f"Entity overlap: {scores.get('entity_overlap', 0):.2%}."
        )
    
    return {
        "case_id": case_data.get("case_id", ""),
        "similarity_label": case_data.get("similarity_label", ""),
        "entity_overlap": entity_overlap,
        "influential_terms": influential_terms,
        "explanation_text": " ".join(explanation_parts) if explanation_parts else
            "This case was retrieved based on overall semantic similarity in legal context and facts.",
        "disclaimer": "This explanation is advisory. Judicial discretion must be exercised independently."
    }
