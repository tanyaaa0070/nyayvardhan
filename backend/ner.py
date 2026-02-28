"""
NyayVandan - Legal Named Entity Recognition (NER)
====================================================
Pipeline Stage 2: Legal Entity Extraction

Extracts legal references from Indian court judgment text:
  - IPC Sections (Indian Penal Code)
  - CrPC Sections (Code of Criminal Procedure)
  - Constitutional Articles
  - Legal Acts / Statutes

Uses a hybrid approach:
  1. spaCy Matcher (rule-based patterns)
  2. Regex fallback for edge cases

⚠️ All processing is LOCAL — no external API calls.
"""

import re
import spacy
from spacy.matcher import Matcher

# ---------- Load spaCy Model ----------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Gracefully degrade if model not downloaded yet
    nlp = spacy.blank("en")

# ---------- Initialize Matcher ----------
matcher = Matcher(nlp.vocab)

# --- IPC Patterns ---
# Matches: "IPC 302", "Section 420 IPC", "IPC Section 302", "I.P.C. 302"
ipc_patterns = [
    [{"LOWER": {"IN": ["ipc"]}}, {"IS_DIGIT": True}],
    [{"LOWER": {"IN": ["ipc"]}}, {"LOWER": "section"}, {"IS_DIGIT": True}],
    [{"LOWER": "section"}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["ipc"]}}],
    [{"LOWER": {"IN": ["ipc"]}}, {"TEXT": {"REGEX": r"^\d+[A-Za-z]?$"}}],
]

# --- CrPC Patterns ---
# Matches: "CrPC 437", "Section 154 CrPC", etc.
crpc_patterns = [
    [{"LOWER": {"IN": ["crpc"]}}, {"IS_DIGIT": True}],
    [{"LOWER": {"IN": ["crpc"]}}, {"LOWER": "section"}, {"IS_DIGIT": True}],
    [{"LOWER": "section"}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["crpc"]}}],
    [{"LOWER": {"IN": ["crpc"]}}, {"TEXT": {"REGEX": r"^\d+[A-Za-z]?$"}}],
]

# --- Constitutional Article Patterns ---
# Matches: "Article 14", "Article 21", "Article 19(1)(a)"
article_patterns = [
    [{"LOWER": "article"}, {"IS_DIGIT": True}],
    [{"LOWER": "article"}, {"TEXT": {"REGEX": r"^\d+[A-Za-z]?$"}}],
]

# Add patterns to matcher
for p in ipc_patterns:
    matcher.add("IPC", [p])
for p in crpc_patterns:
    matcher.add("CRPC", [p])
for p in article_patterns:
    matcher.add("ARTICLE", [p])


# ---------- Regex-Based Extraction (Fallback) ----------
# These catch cases the spaCy matcher might miss

IPC_REGEX = [
    r'IPC\s+(?:Section\s+)?(\d+[A-Za-z]?)',
    r'Section\s+(\d+[A-Za-z]?)\s+(?:of\s+)?(?:the\s+)?(?:Indian\s+Penal\s+Code|IPC)',
    r'(?:Indian\s+Penal\s+Code|I\.P\.C\.?)\s+(\d+[A-Za-z]?)',
    r'u/s\s+(\d+[A-Za-z]?)\s+IPC',
]

CRPC_REGEX = [
    r'CrPC\s+(?:Section\s+)?(\d+[A-Za-z]?)',
    r'Section\s+(\d+[A-Za-z]?)\s+(?:of\s+)?(?:the\s+)?(?:Cr\.?P\.?C\.?|Code\s+of\s+Criminal\s+Procedure)',
    r'Cr\.?P\.?C\.?\s+(\d+[A-Za-z]?)',
    r'u/s\s+(\d+[A-Za-z]?)\s+CrPC',
]

ARTICLE_REGEX = [
    r'Article\s+(\d+[A-Za-z]?(?:\(\d+\)(?:\([a-z]\))?)?)',
    r'Art\.\s*(\d+[A-Za-z]?)',
]

# --- Common Indian Legal Acts ---
ACT_REGEX = [
    r'(Prevention\s+of\s+Corruption\s+Act)',
    r'(POCSO\s+Act)',
    r'(Dowry\s+Prohibition\s+Act)',
    r'(Motor\s+Vehicles\s+Act)',
    r'(Industrial\s+Disputes\s+Act(?:\s+\d{4})?)',
    r'(Information\s+Technology\s+Act)',
    r'(Environment\s+Protection\s+Act(?:\s+\d{4})?)',
    r'(Forest\s+Rights\s+Act(?:\s+\d{4})?)',
    r'(Mines\s+and\s+Minerals\s+Act)',
    r'(Hindu\s+Marriage\s+Act)',
    r'(Rights\s+of\s+Persons\s+with\s+Disabilities\s+Act(?:\s+\d{4})?)',
    r'(Prevention\s+of\s+Money\s+Laundering\s+Act)',
    r'(RERA)',
    r'(POSH\s+Act)',
]


def extract_entities(text: str) -> dict:
    """
    Extract legal entities from case text using hybrid approach.
    
    Combines spaCy rule-based matching with regex fallback
    to ensure comprehensive extraction of legal references.
    
    Args:
        text: Case facts text (raw or cleaned)
    
    Returns:
        dict with keys:
          - IPC_Sections: List of IPC section references
          - CrPC_Sections: List of CrPC section references
          - Constitutional_Articles: List of constitutional articles
          - Acts_Referenced: List of legal acts mentioned
    """
    entities = {
        "IPC_Sections": [],
        "CrPC_Sections": [],
        "Constitutional_Articles": [],
        "Acts_Referenced": []
    }
    
    # --- Phase 1: spaCy Matcher ---
    doc = nlp(text)
    matches = matcher(doc)
    
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span_text = doc[start:end].text
        
        if label == "IPC":
            entities["IPC_Sections"].append(span_text)
        elif label == "CRPC":
            entities["CrPC_Sections"].append(span_text)
        elif label == "ARTICLE":
            entities["Constitutional_Articles"].append(span_text)
    
    # --- Phase 2: Regex Fallback ---
    # IPC
    for pattern in IPC_REGEX:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            section_num = m.group(1)
            normalized = f"IPC {section_num}"
            entities["IPC_Sections"].append(normalized)
    
    # CrPC
    for pattern in CRPC_REGEX:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            section_num = m.group(1)
            normalized = f"CrPC {section_num}"
            entities["CrPC_Sections"].append(normalized)
    
    # Constitutional Articles
    for pattern in ARTICLE_REGEX:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            article_num = m.group(1)
            normalized = f"Article {article_num}"
            entities["Constitutional_Articles"].append(normalized)
    
    # Legal Acts
    for pattern in ACT_REGEX:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            entities["Acts_Referenced"].append(m.group(1))
    
    # --- Phase 3: Deduplicate & Sort ---
    for key in entities:
        entities[key] = sorted(set(entities[key]))
    
    return entities


def extract_sections_from_csv_field(csv_field: str, prefix: str = "") -> list:
    """
    Parse comma-separated section numbers from dataset CSV fields.
    
    Args:
        csv_field: e.g., "302,201,34"
        prefix: e.g., "IPC" → produces ["IPC 302", "IPC 201", "IPC 34"]
    
    Returns:
        List of formatted section strings
    """
    if not csv_field or not isinstance(csv_field, str) or csv_field.strip() == "":
        return []
    
    sections = [s.strip() for s in csv_field.split(",") if s.strip()]
    if prefix:
        return [f"{prefix} {s}" for s in sections]
    return sections
