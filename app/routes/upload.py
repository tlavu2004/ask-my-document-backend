# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services import document_service
from app.config import UPLOAD_DIR
import logging
import json

# Configure logging for this module
logging.basicConfig(level=logging.INFO)  # ensures logs show in console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = True  # allow log to propagate to root logger (uvicorn)

# Try to import PdfReadError from either pypdf or PyPDF2; fall back to a dummy class.
try:
    from pypdf.errors import PdfReadError  # type: ignore
except Exception:
    try:
        from PyPDF2.errors import PdfReadError  # type: ignore
    except Exception:
        class PdfReadError(Exception):  # fallback
            pass

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf"}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Validate extension
    ext = file.filename.lower().rsplit(".", 1)
    if len(ext) < 2 or f".{ext[1]}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        # Save and process
        saved_path, file_id = document_service.save_upload_file(file)
        index_path, metadata_path, chunks = document_service.process_and_index_document(
            saved_path, file_id=file_id
        )

        # If downstream returns empty chunks
        if not chunks or all(not c["content"].strip() for c in chunks):
            raise HTTPException(status_code=422, detail="Empty or no text extracted from PDF.")

        logger.info("Uploaded PDF: %s, file_id: %s, chunks: %d", file.filename, file_id, len(chunks))

        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "index_path": str(index_path),
            "metadata_path": str(metadata_path),
            "message": "File uploaded and indexed successfully."
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PdfReadError as e:
        raise HTTPException(status_code=422, detail=f"Invalid or unreadable PDF: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error during upload: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/{file_id}")
def get_pdf(file_id: str):
    pdf_path = UPLOAD_DIR / f"{file_id}.pdf"

    # Debug logging
    logger.info("UPLOAD_DIR: %s", UPLOAD_DIR)
    logger.info("Checking PDF path: %s", pdf_path)
    logger.info("File exists: %s", pdf_path.exists())

    if not pdf_path.exists():
        logger.warning("PDF not found at: %s", pdf_path)
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(str(pdf_path), media_type="application/pdf")


@router.get("/filename/{file_id}")
def get_filename(file_id: str):
    map_path = UPLOAD_DIR / "file_map.json"
    if not map_path.exists():
        raise HTTPException(status_code=404, detail="File map not found")
    with open(map_path, "r", encoding="utf-8") as f:
        file_map = json.load(f)
    filename = file_map.get(file_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Original filename not found")
    return {"file_id": file_id, "filename": filename}
