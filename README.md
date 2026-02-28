# 🏛️ NyayVandan  
### An Explainable, Ethical & Precedent-Aware AI System for Judicial Decision Support

NyayVandan is an AI-powered **judicial decision support system** designed to assist judges and legal researchers by retrieving **legally relevant precedents with clear explanations and ethical safeguards**.  
The system is strictly **advisory** and preserves **judicial independence** through a human-in-the-loop design.

---

## 🚀 Problem Statement
Indian courts face:
- Massive case backlogs and delayed justice
- Time-consuming manual precedent research
- Inconsistent decisions due to limited access to relevant judgments
- Lack of transparency and ethical safeguards in existing legal AI tools

Most legal AI systems focus on **prediction**, which is unsuitable for judicial use.

---

## 💡 Solution: NyayVandan
NyayVandan shifts AI in law from **prediction → reasoning** by:
- Retrieving **Top-K legally similar precedents**
- Providing **explainable, citeable justifications**
- Detecting **bias and constitutional misalignment**
- Ensuring **human-in-the-loop** decision-making

---

## ✨ Key Features
- 🔍 **Hybrid Case Retrieval** (Semantic + Lexical + Legal Entity based)
- 🧠 **BERT-based Semantic Understanding** (Sentence-BERT)
- ⚖️ **Explainable AI** (LIME & SHAP)
- 🛡️ **Ethical Safeguards** (Bias & Diversity Detection)
- 🇮🇳 **India-Centric Design** (IPC, CrPC, Constitution)
- 👩‍⚖️ **Judge-Centric Dashboard**

---

## 🧠 AI & Algorithms Used

### 1. Natural Language Processing (NLP)
- Text cleaning and normalization
- Sentence segmentation and tokenization

### 2. Legal Named Entity Recognition (NER)
- spaCy with custom legal rules
- Extracts IPC, CrPC, Articles, courts, and case names

### 3. Semantic Embeddings
- **Sentence-BERT (all-MiniLM-L6-v2)**
- Converts case facts into dense semantic vectors

### 4. Lexical Retrieval
- TF-IDF / BM25 for exact legal term matching

### 5. Hybrid Case-Based Reasoning (CBR)
Final similarity score:
<img width="136" height="124" alt="image" src="https://github.com/user-attachments/assets/2daa041f-2c6f-4844-9e9c-8e2ffaa4aa8f" />

Similarity = 0.5 × Semantic + 0.3 × Lexical + 0.2 × Entity Overlap


### 6. Vector Similarity Search
- **FAISS** for fast nearest-neighbor search

### 7. Explainable AI (XAI)
- **LIME** for text influence explanation
- **SHAP** for feature contribution analysis

### 8. Ethical AI
- Diversity Score (bias detection)
- Constitutional alignment checking
- Human-in-the-loop advisory system

---

## 🧩 System Pipeline
<img width="400" height="536" alt="image" src="https://github.com/user-attachments/assets/4cad567e-6a8b-495f-8e27-51f24ec3b68e" />


---

## 🛠️ Technology Stack

### Frontend
- Streamlit (simple, judge-friendly UI)

### Backend
- FastAPI + Uvicorn

### AI / ML
- spaCy
- Sentence-BERT
- FAISS
- TF-IDF / BM25
- LIME
- SHAP

### Dataset
- IndianKanoon judgments (offline)
- Curated constitutional principles dataset

---

## 📊 Performance & Evaluation

| Component | Metric | Result |
|--------|------|--------|
| Legal NER | F1-Score | 0.90 – 0.93 |
| Retrieval Quality | Precision@10 | 0.82 – 0.88 |
| Ranking Quality | NDCG@10 | 0.84 – 0.89 |
| Explainability | Human Rating | 4.2 / 5 |
| Bias Detection | Parity Gap | < 0.1 |

> NyayVandan achieves ~**85% precedent relevance accuracy**.

---

## 🧪 Sample Use Case
- Bail applications (IPC 420, 439 CrPC)
- Sentencing consistency (IPC 302, 304)
- Property and constitutional disputes
- Cybercrime and financial fraud cases

---

## 🔒 Ethical & Legal Safeguards
- No automated decision-making
- No outcome prediction
- Transparent explanations
- Bias alerts and constitutional checks
- Judge retains final authority

---

## 📌 Limitations
- Dependent on digitized judgments
- Requires retraining for legal updates
- GPU recommended for large-scale deployment

---

## 🔮 Future Work
- Multilingual support (Hindi & regional languages)
- High Court / e-Courts pilot integration
- Federated learning for privacy
- Appellate-level explainability
- Voice-based case input

---

## 👨‍💻 Team
- **Tanya Singh**
- **Snigdha**
- **Yashwanti**

**Mentor:** Divyanshu Kumar  
**Domain:** Artificial Intelligence in Law

---

## 📜 Disclaimer
NyayVandan is a **decision-support system** intended to assist legal professionals.  
It does **not replace judicial reasoning or authority**.

---

⭐ *If you find this project useful, please consider starring the repository!*
