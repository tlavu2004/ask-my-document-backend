# app/services/chat_service.py
from app.rag.retriever import get_relevant_context_for_file, rerank_context
from app.rag.rag_pipeline import generate_answer

def handle_query(user_query: str, top_k: int = 2, file_ids: list = None) -> dict:
    """
    Process a user's query:
    1. Retrieve top_k relevant context from EACH FAISS index (each file)
    2. Pass all context + query to LLM for generating answer
    """

    if not user_query.strip():
        raise ValueError("Query cannot be empty.")
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")
    if not file_ids or not isinstance(file_ids, list):
        raise ValueError("file_ids is required and must be a list.")

    # Get top_k context for each file_id
    context_docs = []
    for file_id in file_ids:
        context_docs += get_relevant_context_for_file(user_query, file_id, top_k=top_k)

    # Optionally, limit total context_docs if needed (e.g. max 10)
    # MAX_CONTEXT = 10
    # context_docs = context_docs[:MAX_CONTEXT]

    # Rerank entire context_docs, get top_k most relevant (if any)
    if context_docs:
        context_docs = rerank_context(user_query, context_docs, top_n=top_k)

    # If still blank, we can return a message or pass it to the LLM to answer "I don't know"
    if not context_docs:
        return {
            "query": user_query,
            "context": context_docs,
            "answer": "I don't know"
        }

    answer = generate_answer(user_query, context_docs)

    return {
        "query": user_query,
        "context": context_docs,
        "answer": answer
    }
