import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
DATA_DIR = Path(f"data_{APP_ENV}") if APP_ENV != "dev" else Path("data")

INDEX_DIR = DATA_DIR / "index"
FILE_ID = "mock-file-id"
FAISS_PATH = INDEX_DIR / f"{FILE_ID}.faiss"
META_PATH = INDEX_DIR / f"{FILE_ID}.pkl"

def build_mock_index():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    docs = [
        "Python is a programming language.",
        "FastAPI is a modern, fast web framework for Python.",
        "FAISS is a library for efficient similarity search.",
        "Streamlit is used for building data apps quickly.",
    ]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(docs)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    with open(META_PATH, "wb") as f:
        pickle.dump(docs, f)

    faiss.write_index(index, str(FAISS_PATH))
    print(f"Mock index saved to {FAISS_PATH}")
    print(f"Metadata saved to {META_PATH}")

if __name__ == "__main__":
    build_mock_index()
