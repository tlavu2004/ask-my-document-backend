import pytest
from unittest.mock import patch
from app.services import chat_service

# ===== UNIT TEST (mock retriever + LLM) =====

@pytest.fixture
def mock_context():
    return [
        "Document snippet 1 about Python.",
        "Document snippet 2 about FastAPI.",
        "Document snippet 3 about testing."
    ]

@pytest.fixture
def mock_answer():
    return "This is a mocked LLM answer."

def test_handle_query_returns_expected_keys(mock_context, mock_answer):
    """
    UNIT TEST: Ensure handle_query returns dict with correct keys and values when dependencies are mocked.
    """
    with patch("app.services.chat_service.get_relevant_context_for_file", return_value=mock_context):
        with patch("app.services.chat_service.generate_answer", return_value=mock_answer):
            result = chat_service.handle_query("What is FastAPI?", file_id="mock-file-id")

    assert isinstance(result, dict)
    assert set(result.keys()) == {"query", "context", "answer"}
    assert result["query"] == "What is FastAPI?"
    assert result["context"] == mock_context
    assert result["answer"] == mock_answer

def test_handle_query_calls_dependencies_with_correct_args(mock_context, mock_answer):
    """
    UNIT TEST: Verify get_relevant_context and generate_answer are called with correct arguments.
    """
    with patch("app.services.chat_service.get_relevant_context_for_file", return_value=mock_context) as mock_retriever:
        with patch("app.services.chat_service.generate_answer", return_value=mock_answer) as mock_llm:
            chat_service.handle_query("Explain pytest", top_k=5, file_id="mock-file-id")

    mock_retriever.assert_called_once_with("Explain pytest", "mock-file-id", top_k=5)
    mock_llm.assert_called_once_with("Explain pytest", mock_context)

def test_handle_query_with_empty_results(mock_answer):
    """
    UNIT TEST: Handle case where retriever returns no documents.
    """
    with patch("app.services.chat_service.get_relevant_context_for_file", return_value=[]):
        with patch("app.services.chat_service.generate_answer", return_value=mock_answer):
            result = chat_service.handle_query("Unknown topic", file_id="mock-file-id")

    assert result["context"] == []
    assert result["answer"] == mock_answer

# ===== INTEGRATION TEST (mock index thật) =====

@pytest.mark.usefixtures("build_mock_faiss_index")
def test_handle_query_integration_with_mock_index():
    """
    INTEGRATION TEST: Use real mock FAISS index and ensure handle_query works end-to-end (retriever + LLM).
    LLM output is still mocked to keep test deterministic.
    """
    fake_answer = "Mocked integration answer."
    with patch("app.services.chat_service.generate_answer", return_value=fake_answer):
        result = chat_service.handle_query("What is Python?", top_k=2, file_id="mock-file-id")

    assert isinstance(result["context"], list)
    assert len(result["context"]) > 0
    assert result["answer"] == fake_answer
    # Ensure that the returned context contains relevant text
    assert any("Python" in doc for doc in result["context"])
