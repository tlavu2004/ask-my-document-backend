# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, query
from dotenv import load_dotenv

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Ask My Document",
        description="Upload documents and ask questions using RAG pipeline.",
        version="0.1.0",
    )

    # CORS middleware for Swagger UI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # hoặc giới hạn domain cụ thể
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload.router, prefix="/documents", tags=["Upload"])
    app.include_router(query.router, prefix="/documents", tags=["Query"])

    return app

app = create_app()
