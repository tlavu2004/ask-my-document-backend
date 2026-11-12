# tests/routes/test_query.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_query_route_returns_expected_fields():
    payload = {"query": "What is Python?", "top_k": 2, "file_id": "mock-file-id"}
    # Mock handle_query for returning fixed values, avoiding real logic that may cause 500 errors
    with patch("app.services.chat_service.handle_query") as mock_handle_query:
        mock_handle_query.return_value = {
            "query": payload["query"],
            "context": ["mocked context 1", "mocked context 2"],
            "answer": "mocked answer"
        }
        response = client.post("/documents/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert "context" in data
    assert "answer" in data

def test_query_route_missing_query_field():
    """
    Missing 'query' → should return 422 Unprocessable Entity (FastAPI validation error)
    """
    payload = {"top_k": 2}  # 'query' is missing
    response = client.post("/documents/query", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"][-1] == "query"

def test_query_route_negative_top_k():
    """
    Negative top_k → should return 422 due to validation error
    """
    payload = {"query": "Test", "top_k": -3}
    response = client.post("/documents/query", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"][-1] == "top_k"

def test_query_route_empty_context(monkeypatch):
    """
    Mock retriever to return empty list → context should be empty but still 200 OK
    """
    from app.services import chat_service

    def mock_handle_query(query, top_k, file_id=None):
        return {"query": query, "context": [], "answer": "No relevant documents found."}

    monkeypatch.setattr(chat_service, "handle_query", mock_handle_query)

    payload = {"query": "Random string that matches nothing", "top_k": 2, "file_id": "mock-file-id"}
    response = client.post("/documents/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["context"] == []
    assert "No relevant documents found" in data["answer"]

def test_query_route_llm_error(monkeypatch):
    """
    Mock handle_query to raise an exception → should return 500 Internal Server Error
    """
    from app.services import chat_service

    def mock_handle_query(query, top_k, file_id=None):
        raise RuntimeError("LLM service unavailable")

    monkeypatch.setattr(chat_service, "handle_query", mock_handle_query)

    payload = {"query": "Test", "top_k": 2, "file_id": "mock-file-id"}
    response = client.post("/documents/query", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert "LLM service unavailable" in data["error"]
