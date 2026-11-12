# app/rag/rag_pipeline.py
from typing import List
from app.rag.retriever import FaissRetriever

def build_prompt(query: str, context_docs: List[str]) -> str:
    """
    Build prompt for LLM from query and context documents.
    """
    context_text = "\n".join(context_docs)
    return (
        "You are an assistant answering based on the provided documents.\n"
        "Context:\n"
        f"{context_text}\n\n"
        "Question:\n"
        f"{query}\n\n"
        "Answer:"
    )

class RAGPipeline:
    def __init__(self, index_path: str, metadata_path: str, llm_client):
        """
        llm_client: object with method `generate(prompt: str) -> str`
        """
        self.retriever = FaissRetriever(index_path, metadata_path)
        self.llm_client = llm_client

    def run(self, query: str, top_k: int = 5) -> str:
        # Get context from FAISS
        context_chunks: List[str] = self.retriever.retrieve(query, top_k=top_k)
        
        # Build prompt
        prompt = build_prompt(query, context_chunks)
        
        # Call LLM
        answer = self.llm_client.generate(prompt)
        return answer

def generate_answer(query: str, context_docs: list[dict], llm_client=None) -> str:
    """
    Generate answer from query and context using LLM.
    """
    if llm_client is None:
        from app.utils.llm_client import get_default_llm
        llm_client = get_default_llm()

    # Only get the content of the context
    context_texts = [c["content"] for c in context_docs]
    return llm_client.generate(query, context_texts)
