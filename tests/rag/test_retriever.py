# tests/rag/test_retriever.py
import os
from pathlib import Path
from app.rag.retriever import FaissRetriever

def test_retriever_returns_results():
    APP_ENV = os.getenv("APP_ENV", "dev")
    DATA_DIR = Path(f"data_{APP_ENV}") if APP_ENV != "dev" else Path("data")
    file_id = "mock-file-id"
    index_path = DATA_DIR / "index" / f"{file_id}.faiss"
    meta_path = DATA_DIR / "index" / f"{file_id}.pkl"

    assert index_path.exists(), f"FAISS index file missing: {index_path}"
    assert meta_path.exists(), f"Metadata file missing: {meta_path}"

    retriever = FaissRetriever(index_path, meta_path)
    results = retriever.retrieve("What is Python?", top_k=2)

    assert isinstance(results, list), "Results should be a list"
    assert len(results) > 0, "No results returned"
    assert any("Python" in r or "programming" in r for r in results), \
        "Relevant content not found in results"

    print("Retriever test passed. Sample results:", results)
