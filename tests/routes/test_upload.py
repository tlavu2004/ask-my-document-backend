# tests/routes/test_upload.py
from fastapi.testclient import TestClient
from app.main import app
from app.config import UPLOAD_DIR, INDEX_DIR
import shutil

client = TestClient(app)

# def clean_dirs():
#     """Ensure upload and index directories are clean before each test."""
#     for d in [UPLOAD_DIR, INDEX_DIR]:
#         if d.exists():
#             shutil.rmtree(d)
#         d.mkdir(parents=True, exist_ok=True)

def test_upload_non_pdf_should_fail(tmp_path):
    # clean_dirs()

    fake_txt = tmp_path / "fake.txt"
    fake_txt.write_text("This is not a PDF file.")

    with fake_txt.open("rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("fake.txt", f, "text/plain")}
        )

    json_data = response.json()
    assert response.status_code == 415
    assert "unsupported file type" in json_data["detail"].lower()

def test_upload_pdf(sample_pdf_path):
    # clean_dirs()

    with sample_pdf_path.open("rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("sample.pdf", f, "application/pdf")}
        )

    json_data = response.json()
    assert response.status_code == 200
    assert json_data["status"].lower() == "success"
    assert json_data["filename"] == "sample.pdf"
    assert isinstance(json_data["chunks"], int) and json_data["chunks"] > 0
    assert json_data["index_path"].endswith(".faiss")
    assert "uploaded and indexed successfully" in json_data["message"].lower()

    # Verify file saved
    file_id = json_data.get("file_id")
    assert file_id is not None
    assert any(file_id in p.name for p in UPLOAD_DIR.iterdir())

    # Verify index files created
    assert any(p.suffix == ".faiss" for p in INDEX_DIR.iterdir())
    assert any(p.suffix == ".pkl" for p in INDEX_DIR.iterdir())

def test_upload_empty_pdf_should_fail(tmp_path):
    # clean_dirs()

    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b"%PDF-1.4\n%EOF")  # minimal empty PDF

    with empty_pdf.open("rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("empty.pdf", f, "application/pdf")}
        )

    json_data = response.json()
    assert response.status_code in (400, 422)
    assert (
        "empty" in json_data["detail"].lower()
        or "no text" in json_data["detail"].lower()
        or "invalid or unreadable pdf" in json_data["detail"].lower()
        or "eof marker not found" in json_data["detail"].lower()
    )

def test_upload_large_pdf(tmp_path):
    # clean_dirs()

    from reportlab.pdfgen import canvas
    large_pdf_path = tmp_path / "large.pdf"
    c = canvas.Canvas(str(large_pdf_path))
    for i in range(100):
        c.drawString(100, 750, f"This is line {i} of the large PDF for testing chunking.")
        c.showPage()
    c.save()

    with large_pdf_path.open("rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("large.pdf", f, "application/pdf")}
        )

    json_data = response.json()
    assert response.status_code == 200
    assert json_data["status"].lower() == "success"
    assert json_data["chunks"] > 1
    assert json_data["index_path"].endswith(".faiss")
