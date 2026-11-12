# tests/rag/test_rag_pipeline.py
import os
from pathlib import Path
from app.rag.rag_pipeline import RAGPipeline

class MockLLM:
    def generate(self, prompt: str) -> str:
        return f"[MOCK ANSWER] Prompt received:\n{prompt}"

def test_pipeline_runs_with_mock_llm():
    APP_ENV = os.getenv("APP_ENV", "dev")
    DATA_DIR = Path(f"data_{APP_ENV}") if APP_ENV != "dev" else Path("data")
    file_id = "mock-file-id"
    index_path = DATA_DIR / "index" / f"{file_id}.faiss"
    meta_path = DATA_DIR / "index" / f"{file_id}.pkl"

    assert index_path.exists(), f"FAISS index file missing: {index_path}"
    assert meta_path.exists(), f"Metadata file missing: {meta_path}"

    pipeline = RAGPipeline(index_path, meta_path, llm_client=MockLLM())
    answer = pipeline.run("What is FastAPI?", top_k=2)

    assert isinstance(answer, str), "Pipeline output should be a string"
    assert "[MOCK ANSWER]" in answer, "Mock LLM response not detected"
    assert "FastAPI" in answer or "Prompt received" in answer, \
        "Expected keyword not found in answer"

    print("Pipeline test passed. Sample answer:", answer)
