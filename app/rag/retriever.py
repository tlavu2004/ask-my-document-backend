# app/rag/retriever.py
import os
from pathlib import Path
import faiss
import pickle
from typing import List
from sentence_transformers import SentenceTransformer, CrossEncoder

# ==== Config: dynamic data folder based on APP_ENV ====
APP_ENV = os.getenv("APP_ENV", "dev")  # default dev
DATA_DIR = Path(f"data_{APP_ENV}") if APP_ENV != "dev" else Path("data")
INDEX_DIR = DATA_DIR / "index"

class FaissRetriever:
    def __init__(self, index_path: Path, metadata_path: Path):
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f"FAISS index or metadata not found: {index_path}, {metadata_path}")

        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        query_emb = self.embed_model.encode([query])
        distances, indices = self.index.search(query_emb, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results


def build_faiss_index(docs: list[dict], index_path: Path, metadata_path: Path):
    # docs: list of dict: {"content": ..., "file_id": ..., "file_name": ..., "page_number": ...}
    index_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model.encode([doc["content"] for doc in docs])

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, str(index_path))
    with open(metadata_path, "wb") as f:
        pickle.dump(docs, f)


# ==== Default mock paths for quick retrieval ====
INDEX_PATH = INDEX_DIR / "mock_index.faiss"
META_PATH = INDEX_DIR / "mock_index.pkl"

def get_relevant_context(query: str, top_k: int = 2):
    retriever = FaissRetriever(INDEX_PATH, META_PATH)
    return retriever.retrieve(query, top_k)

def get_relevant_context_for_file(query: str, file_id: str, top_k: int = 2, threshold: float = None):
    index_path = INDEX_DIR / f"{file_id}.faiss"
    meta_path = INDEX_DIR / f"{file_id}.pkl"
    retriever = FaissRetriever(index_path, meta_path)
    query_emb = retriever.embed_model.encode([query])
    distances, indices = retriever.index.search(query_emb, top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and (threshold is None or dist < threshold):
            results.append(retriever.metadata[idx])
    return results

# Add cross-encoder model for reranking
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_context(query: str, context_chunks: list[dict], top_n: int = 2) -> list[dict]:
    if not context_chunks:
        return []
    pairs = [(query, chunk["content"]) for chunk in context_chunks]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(scores, context_chunks), key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in ranked[:min(top_n, len(ranked))]]
