# tests/conftest.py
import sys
import os
import pytest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from tests.utils.build_mock_index import build_mock_index

# Import make_pdf function from scripts/make_sample_pdf.py
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.append(str(SCRIPTS_DIR))
from scripts.make_sample_pdf import make_pdf

@pytest.fixture(scope="session")
def build_mock_faiss_index():
    """
    Build a mock FAISS index before running tests that depend on it.
    """
    build_mock_index()
    yield

@pytest.fixture
def sample_pdf_path(tmp_path):
    """
    Create a sample PDF in a temporary path using scripts/make_sample_pdf.py
    """
    pdf_path = tmp_path / "sample.pdf"
    make_pdf(pdf_path)
    return pdf_path
