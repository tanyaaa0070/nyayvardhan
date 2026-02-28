# ⚖️ NyayVandan — Judicial Decision Support System

> *"NyayVandan assists judicial reasoning by retrieving, explaining, and ethically evaluating similar legal precedents using offline AI models — without predicting outcomes or replacing human judgment."*

## 🏛 Overview

NyayVandan is a **judge-centric, offline-first** system that:
- **Retrieves** similar Indian legal precedents using hybrid AI (Sentence-BERT + TF-IDF + Legal Entity matching)
- **Explains** why each precedent is similar via overlapping facts, legal sections, and influential terms
- **Evaluates** the precedent set for ethical concerns, bias indicators, and constitutional alignment

### ⚠️ NyayVandan is ADVISORY ONLY
- ❌ No predictions
- ❌ No probability scores
- ❌ No automation of judicial decisions
- ✅ Judge-readable, citeable outputs

---

## 📁 Project Structure

```
nyayvardhan-main/
├── backend/
│   ├── __init__.py          # Package init
│   ├── app.py               # FastAPI REST API server
│   ├── config.py            # Centralized configuration
│   ├── preprocessor.py      # Stage 1: Text cleaning & tokenization
│   ├── ner.py               # Stage 2: Legal NER (IPC, CrPC, Articles)
│   ├── embeddings.py        # Stage 3: Sentence-BERT + FAISS index
│   ├── retriever.py         # Stage 4: Hybrid case retrieval (CBR)
│   ├── explainability.py    # Stage 5: Similarity explanations
│   └── ethics.py            # Stage 6: Bias detection & constitutional alignment
├── data/
│   ├── generate_sample_data.py   # Sample dataset generator
│   ├── judgments.csv              # Case dataset (30 sample cases)
│   ├── embeddings.faiss           # FAISS index (auto-generated)
│   └── embeddings.npy             # Cached embeddings (auto-generated)
├── frontend/
│   ├── index.html           # Complete UI (Landing + Login + Dashboard)
│   ├── styles.css           # Dark judicial theme (black + brown + gold)
│   └── app.js               # Frontend application logic
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Start the Backend Server

```bash
python run.py
```

The server starts at `http://localhost:8000`.  
API docs: `http://localhost:8000/docs`

On first run, the system will:
- Generate sample dataset (if not present)
- Download Sentence-BERT model (~80MB, cached locally)
- Build FAISS index from the dataset

### 3. Open the Frontend

Open `frontend/index.html` in your browser.

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI |
| Embeddings | Sentence-BERT (all-MiniLM-L6-v2, local) |
| Search | FAISS (local similarity index) |
| NER | spaCy (rule-based + regex legal patterns) |
| Lexical | TF-IDF (scikit-learn) |
| Explainability | LIME, TF-IDF term analysis |
| Data | Pandas, local CSV |
| Frontend | HTML + CSS + Vanilla JavaScript |

---

## 🔐 Constraints

- ❌ No external or paid APIs (No OpenAI, No IndianKanoon, No NJDG)
- ✅ All models run locally
- ✅ 100% offline execution
- ✅ Dataset-driven (Kaggle-compatible format)
