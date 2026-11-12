from app.utils.llm_client import get_default_llm

def test_mock_llm_generate():
    llm = get_default_llm()
    question = "Hello, what is Python?"
    context_docs = ["Python is a programming language.", "It is used for many applications."]
    result = llm.generate(question, context_docs)
    assert isinstance(result, str)
