# app/services/document_service.py
from pathlib import Path
from fastapi import UploadFile
import uuid
import json

from app.config import UPLOAD_DIR, INDEX_DIR
from app.utils.pdf_parser import extract_text_chunks
from app.rag.retriever import build_faiss_index

from langchain.text_splitter import RecursiveCharacterTextSplitter

def save_upload_file(file: UploadFile, upload_dir: Path = UPLOAD_DIR) -> Path:
    """
    Save the uploaded file to the given upload_dir with original filename.
    Automatically uses separate folders for prod/test depending on APP_ENV.
    """
    file_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix
    file_path = upload_dir / f"{file_id}{ext}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    update_file_map(file_id, file.filename)
    return file_path, file_id

def split_text_to_docs(pages: list[dict], file_id: str, file_name: str, chunk_size: int = 500) -> list[dict]:
    """
    Split text from PDF pages into smaller chunks for indexing.
    """
    docs = []
    for page in pages:
        page_number = page["page_number"]
        text = page["content"]
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]
            docs.append({
                "file_id": file_id,
                "file_name": file_name,
                "page_number": page_number,
                "content": chunk_text
            })
    return docs

def create_faiss_index_and_save(docs: list[dict], index_path: Path, metadata_path: Path):
    """
    Build FAISS index from docs and save both index and metadata to disk.
    """
    build_faiss_index(docs, index_path, metadata_path)

def process_and_index_document(file_path: Path, file_id: str):
    """
    Extract text from PDF, split into chunks, and build FAISS index.
    Index/metadata are saved using file_id.
    """
    text = extract_text_chunks(file_path)

    if not text or all(not page["content"].strip() for page in text):
        raise ValueError("Empty or no text extracted from PDF.")

    chunks = split_text_to_docs(text, file_id, file_path.name)
    if not chunks or all(not c["content"].strip() for c in chunks):
        raise ValueError("Empty or no text extracted from PDF.")

    index_path = INDEX_DIR / f"{file_id}.faiss"
    metadata_path = INDEX_DIR / f"{file_id}.pkl"
    create_faiss_index_and_save(chunks, index_path, metadata_path)
    return index_path, metadata_path, chunks

def update_file_map(file_id: str, original_name: str):
    map_path = UPLOAD_DIR / "file_map.json"
    file_map = {}
    if map_path.exists():
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    file_map = json.loads(content)
        except Exception:
            file_map = {}
    file_map[file_id] = original_name
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(file_map, f, ensure_ascii=False, indent=2)
