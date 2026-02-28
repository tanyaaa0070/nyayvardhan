"""
NyayVandan - Unified Dataset Loader
======================================
Loads, normalizes, and merges data from 4 Kaggle datasets into a single
unified format that the backend pipeline can consume.

Datasets integrated:
  1. CivilSum (train.csv)         → Indian legal documents with summaries
  2. Constitution of India (CSV)  → Articles 1-395 for knowledge enrichment
  3. IPC QA (JSON)                → IPC question-answer pairs
  4. CrPC QA (JSON)               → CrPC question-answer pairs
  5. Constitution QA (JSON)       → Constitution question-answer pairs
  6. Sample judgments (judgments.csv) → Our generated sample dataset

The unified output has these columns:
  case_id, case_title, case_text, court, year,
  ipc_sections, crpc_sections, constitutional_articles,
  judgment_outcome, source
"""

import os
import re
import json
import pandas as pd
import numpy as np

from backend.config import DATA_DIR


# ===================== LOADERS FOR EACH DATASET =====================


def load_civilsum(max_rows=500):
    """
    Load CivilSum dataset (train.csv) — Indian legal document summarisation.
    
    Columns: doc_id, text, summary
    We use 'text' as case_text and 'summary' for enrichment.
    We limit to max_rows to keep embedding time reasonable.
    """
    train_path = os.path.join(DATA_DIR, "train.csv")
    if not os.path.exists(train_path):
        print("  [SKIP] train.csv not found")
        return pd.DataFrame()
    
    print(f"  Loading CivilSum (train.csv), limit={max_rows}...")
    df = pd.read_csv(train_path, nrows=max_rows)
    
    rows = []
    for _, row in df.iterrows():
        text = str(row.get("text", ""))
        summary = str(row.get("summary", ""))
        doc_id = str(row.get("doc_id", ""))
        
        if len(text) < 50:
            continue
        
        # Try to extract court name from text
        court = extract_court_from_text(text)
        
        # Try to extract year from text
        year = extract_year_from_text(text)
        
        # Extract IPC/CrPC/Articles from text
        ipc = extract_ipc_from_text(text)
        crpc = extract_crpc_from_text(text)
        articles = extract_articles_from_text(text)
        
        # Try to extract outcome from summary or text
        outcome = extract_outcome_from_text(summary + " " + text)
        
        # Build a title from summary (first 80 chars)
        title = summary[:80].strip() + "..." if len(summary) > 80 else summary.strip()
        
        rows.append({
            "case_id": f"CS-{doc_id}",
            "case_title": title if title else f"CivilSum Case {doc_id}",
            "case_text": text,
            "court": court,
            "year": year,
            "ipc_sections": ",".join(ipc),
            "crpc_sections": ",".join(crpc),
            "constitutional_articles": ",".join(articles),
            "judgment_outcome": outcome,
            "source": "civilsum"
        })
    
    result = pd.DataFrame(rows)
    print(f"  Loaded {len(result)} cases from CivilSum")
    return result


def load_constitution_articles():
    """
    Load Constitution of India articles.
    These are NOT case records — they are used to enrich constitutional alignment.
    Returns a lookup dict: article_number -> article_text
    """
    csv_path = os.path.join(DATA_DIR, "Constitution Of India.csv")
    if not os.path.exists(csv_path):
        print("  [SKIP] Constitution Of India.csv not found")
        return {}
    
    print("  Loading Constitution of India articles...")
    df = pd.read_csv(csv_path)
    
    articles = {}
    for _, row in df.iterrows():
        text = str(row.get("Articles", ""))
        # Try to extract article number from start of text
        match = re.match(r'^(\d+[A-Za-z]?)\.\s*(.+)', text, re.DOTALL)
        if match:
            art_num = match.group(1)
            art_text = match.group(2).strip()
            articles[art_num] = art_text
    
    print(f"  Loaded {len(articles)} constitutional articles")
    return articles


def load_legal_qa(filename, source_label, prefix):
    """
    Load a legal QA JSON file (IPC/CrPC/Constitution).
    Convert Q&A pairs into pseudo-case records for the knowledge base.
    
    Args:
        filename: JSON filename (e.g., "ipc_qa.json")
        source_label: Source tag (e.g., "ipc_qa")
        prefix: Section prefix (e.g., "IPC")
    """
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filename} not found")
        return pd.DataFrame()
    
    print(f"  Loading {filename}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rows = []
    for i, item in enumerate(data):
        question = str(item.get("question", ""))
        answer = str(item.get("answer", ""))
        
        combined_text = f"Legal Question: {question}\nLegal Answer: {answer}"
        
        if len(combined_text) < 30:
            continue
        
        # Extract section numbers from text
        sections = []
        if prefix == "IPC":
            sections = extract_ipc_from_text(combined_text)
        elif prefix == "CrPC":
            sections = extract_crpc_from_text(combined_text)
        
        articles = extract_articles_from_text(combined_text)
        
        rows.append({
            "case_id": f"{prefix}QA-{i+1:04d}",
            "case_title": question[:80] + ("..." if len(question) > 80 else ""),
            "case_text": combined_text,
            "court": "Legal Reference",
            "year": 0,
            "ipc_sections": ",".join(sections) if prefix == "IPC" else "",
            "crpc_sections": ",".join(sections) if prefix == "CrPC" else "",
            "constitutional_articles": ",".join(articles),
            "judgment_outcome": "Reference Material",
            "source": source_label
        })
    
    result = pd.DataFrame(rows)
    print(f"  Loaded {len(result)} entries from {filename}")
    return result


def load_sample_judgments():
    """Load our sample judgments.csv (the 30 hand-crafted cases)."""
    path = os.path.join(DATA_DIR, "judgments.csv")
    if not os.path.exists(path):
        print("  [SKIP] judgments.csv not found")
        return pd.DataFrame()
    
    print("  Loading sample judgments.csv...")
    df = pd.read_csv(path)
    df["source"] = "sample"
    print(f"  Loaded {len(df)} sample cases")
    return df


# ===================== TEXT EXTRACTION HELPERS =====================


def extract_court_from_text(text):
    """Try to extract the court name from legal text."""
    court_patterns = [
        (r"Supreme Court of India", "Supreme Court of India"),
        (r"Supreme Court", "Supreme Court of India"),
        (r"High Court of ([A-Za-z\s&]+?)(?:\s+at|\s*,|\s*-|\.|$)", None),
        (r"([\w\s]+)\s+High Court", None),
        (r"(Delhi|Bombay|Madras|Calcutta|Allahabad|Karnataka|Kerala|Gujarat|Rajasthan|Punjab|Patna|Gauhati|Orissa|Jharkhand|Chhattisgarh|Uttarakhand|Telangana|Andhra Pradesh|Madhya Pradesh|Himachal Pradesh)\s+High Court", None),
        (r"Sessions Court", "Sessions Court"),
        (r"District Court", "District Court"),
        (r"Tribunal", "Tribunal"),
    ]
    
    for pattern, fixed_name in court_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if fixed_name:
                return fixed_name
            else:
                court_name = match.group(1).strip() if match.lastindex else match.group(0).strip()
                return f"{court_name} High Court" if "High Court" not in court_name else court_name
    
    return "Unknown Court"


def extract_year_from_text(text):
    """Extract the most likely judgment year from text."""
    # Look for year patterns near judgment-related words
    matches = re.findall(r'(?:19|20)\d{2}', text[:500])  # Search only first 500 chars
    if matches:
        years = [int(y) for y in matches if 1950 <= int(y) <= 2025]
        if years:
            return max(years)  # Most recent year is likely the judgment year
    return 0


def extract_ipc_from_text(text):
    """Extract IPC section numbers from text."""
    sections = set()
    patterns = [
        r'(?:Section|Sec\.?|S\.)\s*(\d+[A-Za-z]?)\s*(?:of\s+)?(?:the\s+)?(?:Indian\s+Penal\s+Code|IPC|I\.P\.C)',
        r'(?:IPC|I\.P\.C\.?)\s*(?:Section|Sec\.?)?\s*(\d+[A-Za-z]?)',
        r'(?:Sections?)\s+([\d,\s]+(?:and\s+\d+)?)\s+(?:IPC|I\.P\.C)',
    ]
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            nums = re.findall(r'\d+[A-Za-z]?', m.group(1))
            sections.update(nums)
    return sorted(sections)


def extract_crpc_from_text(text):
    """Extract CrPC section numbers from text."""
    sections = set()
    patterns = [
        r'(?:Section|Sec\.?|S\.)\s*(\d+[A-Za-z]?)\s*(?:of\s+)?(?:the\s+)?(?:Cr\.?P\.?C|Code\s+of\s+Criminal\s+Procedure)',
        r'(?:Cr\.?P\.?C\.?)\s*(?:Section|Sec\.?)?\s*(\d+[A-Za-z]?)',
        r'(?:CrPC)\s+(\d+[A-Za-z]?)',
    ]
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            nums = re.findall(r'\d+[A-Za-z]?', m.group(1))
            sections.update(nums)
    return sorted(sections)


def extract_articles_from_text(text):
    """Extract Constitutional Article numbers from text."""
    articles = set()
    patterns = [
        r'Article\s+(\d+[A-Za-z]?)',
        r'Art\.\s*(\d+[A-Za-z]?)',
    ]
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            articles.add(m.group(1))
    return sorted(articles)


def extract_outcome_from_text(text):
    """Try to determine judgment outcome from text."""
    text_lower = text.lower()
    
    outcome_patterns = [
        (r"appeal\s+(?:is\s+)?dismissed", "Appeal Dismissed"),
        (r"petition\s+(?:is\s+)?dismissed", "Petition Dismissed"),
        (r"appeal\s+(?:is\s+)?allowed", "Appeal Allowed"),
        (r"petition\s+(?:is\s+)?allowed", "Petition Allowed"),
        (r"writ\s+petition\s+(?:is\s+)?dismissed", "Writ Dismissed"),
        (r"writ\s+petition\s+(?:is\s+)?allowed", "Writ Allowed"),
        (r"bail\s+(?:is\s+)?granted", "Bail Granted"),
        (r"bail\s+(?:is\s+)?rejected", "Bail Rejected"),
        (r"convicted", "Convicted"),
        (r"acquitted", "Acquitted"),
        (r"(?:is\s+)?set\s+aside", "Set Aside"),
        (r"partly\s+allowed", "Partially Allowed"),
    ]
    
    for pattern, outcome in outcome_patterns:
        if re.search(pattern, text_lower):
            return outcome
    
    return "Refer to Full Text"


# ===================== MAIN UNIFIED LOADER =====================


def load_unified_dataset(civilsum_limit=500):
    """
    Load and merge all available datasets into a single unified DataFrame.
    
    Args:
        civilsum_limit: Max rows to load from CivilSum (to control size)
    
    Returns:
        tuple: (unified_df, constitution_articles_dict)
    """
    print("=" * 60)
    print("  NyayVandan - Unified Dataset Loader")
    print("=" * 60)
    
    frames = []
    
    # 1. Sample judgments (always include)
    sample_df = load_sample_judgments()
    if len(sample_df) > 0:
        frames.append(sample_df)
    
    # 2. CivilSum cases
    civil_df = load_civilsum(max_rows=civilsum_limit)
    if len(civil_df) > 0:
        frames.append(civil_df)
    
    # 3. IPC QA knowledge base
    ipc_df = load_legal_qa("ipc_qa.json", "ipc_qa", "IPC")
    if len(ipc_df) > 0:
        frames.append(ipc_df)
    
    # 4. CrPC QA knowledge base
    crpc_df = load_legal_qa("crpc_qa.json", "crpc_qa", "CrPC")
    if len(crpc_df) > 0:
        frames.append(crpc_df)
    
    # 5. Constitution QA knowledge base
    const_df = load_legal_qa("constitution_qa.json", "constitution_qa", "Article")
    if len(const_df) > 0:
        frames.append(const_df)
    
    # 6. Constitution articles (returned as lookup dict, not merged into cases)
    constitution_lookup = load_constitution_articles()
    
    # Merge all frames
    if frames:
        unified = pd.concat(frames, ignore_index=True)
    else:
        unified = pd.DataFrame()
    
    # Ensure required columns exist with defaults
    required_cols = {
        "case_id": "", "case_title": "", "case_text": "",
        "court": "Unknown", "year": 0,
        "ipc_sections": "", "crpc_sections": "",
        "constitutional_articles": "", "judgment_outcome": "",
        "source": "unknown"
    }
    for col, default in required_cols.items():
        if col not in unified.columns:
            unified[col] = default
        unified[col] = unified[col].fillna(default)
    
    # Convert year to int
    unified["year"] = pd.to_numeric(unified["year"], errors="coerce").fillna(0).astype(int)
    
    # Remove rows with very short text (< 30 chars)
    unified = unified[unified["case_text"].str.len() >= 30].reset_index(drop=True)
    
    print(f"\n{'=' * 60}")
    print(f"  UNIFIED DATASET SUMMARY")
    print(f"  Total records: {len(unified)}")
    print(f"  By source:")
    for src, count in unified["source"].value_counts().items():
        print(f"    - {src}: {count}")
    print(f"{'=' * 60}\n")
    
    return unified, constitution_lookup


# ===================== ENTRY POINT =====================

if __name__ == "__main__":
    df, const = load_unified_dataset(civilsum_limit=200)
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Constitution articles loaded: {len(const)}")
    
    # Save unified dataset
    output_path = os.path.join(DATA_DIR, "unified_judgments.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved to {output_path}")
