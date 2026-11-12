from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_chunks(file_path: Path, chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    """
    Load PDF, split into chunks, and keep metadata (page, file).
    Returns: list of dict with keys: content, page_number, file_name
    """
    loader = PyPDFLoader(str(file_path))
    documents = loader.load()  # Each document has .page_content and .metadata['page']

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)

    results = []
    for chunk in chunks:
        results.append({
            "content": chunk.page_content,
            "page_number": chunk.metadata.get("page", None),
            "file_name": file_path.name
        })
    return results
