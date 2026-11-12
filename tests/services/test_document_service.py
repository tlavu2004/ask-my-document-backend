from pathlib import Path
import os
import shutil
import pytest
from fastapi import UploadFile
from app.services import document_service
from app.utils import pdf_parser

# Read APP_ENV, default to "dev"
APP_ENV = os.getenv("APP_ENV", "dev")
DATA_DIR = Path(f"data_{APP_ENV}") if APP_ENV != "dev" else Path("data")

# Test directories (inside env-specific data folder)
UPLOAD_DIR = DATA_DIR / "uploads" / "test"
INDEX_DIR = DATA_DIR / "index" / "test"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Set up test directories
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    yield

    # Cleanup test directories
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)

def test_save_upload_file(tmp_path):
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"%PDF-1.4 sample pdf content")

    upload_file = UploadFile(filename="sample.pdf", file=open(file_path, "rb"))
    saved_path, file_id = document_service.save_upload_file(upload_file, upload_dir=UPLOAD_DIR)
    assert saved_path.exists()
    assert file_id is not None

def test_extract_text(tmp_path):
    sample_pdf_path = Path("tests/resources/sample.pdf")
    if not sample_pdf_path.exists():
        pytest.skip("Sample PDF file not found, skipping text extraction test.")
    
    text = pdf_parser.extract_text_chunks(sample_pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0

def test_create_faiss_index_and_save(tmp_path):
    docs = ["This is a test document.", "Another document for indexing."]
    index_path = INDEX_DIR / "test_index.faiss"
    metadata_path = INDEX_DIR / "test_index.pkl"

    document_service.create_faiss_index_and_save(docs, index_path, metadata_path)

    assert index_path.exists()
    assert metadata_path.exists()

def test_full_document_process(tmp_path):
    sample_pdf_path = "tests/resources/sample.pdf"
    if not os.path.exists(sample_pdf_path):
        pytest.skip("Sample PDF file not found, skipping full document process test.")

    with open(sample_pdf_path, "rb") as f:
        upload_file = UploadFile(filename="sample.pdf", file=f)
        saved_path, file_id = document_service.save_upload_file(upload_file, upload_dir=UPLOAD_DIR)

    text = pdf_parser.extract_text_chunks(saved_path)
    docs = document_service.split_text_to_docs(text)

    index_path = INDEX_DIR / "sample_index.faiss"
    metadata_path = INDEX_DIR / "sample_index.pkl"

    document_service.create_faiss_index_and_save(docs, index_path, metadata_path)

    assert saved_path.exists()
    assert index_path.exists()
    assert metadata_path.exists()
