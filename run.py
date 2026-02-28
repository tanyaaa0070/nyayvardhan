"""
NyayVandan - Application Runner
=================================
Start the backend server with a single command.

Usage:
    python run.py

Prerequisites:
    1. pip install -r requirements.txt
    2. python -m spacy download en_core_web_sm

The server will start on http://localhost:8000
API docs available at http://localhost:8000/docs
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("  NyayVandan — Judicial Decision Support System")
    print("  Starting server...")
    print("=" * 60)
    
    # Check if dataset exists, generate if not
    from backend.config import JUDGMENTS_CSV
    if not os.path.exists(JUDGMENTS_CSV):
        print("\n📂 Dataset not found. Generating sample data...")
        from data.generate_sample_data import generate_dataset
        generate_dataset()
    
    # Start the FastAPI server
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
