from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from fastapi.responses import JSONResponse
from app.services import chat_service

router = APIRouter()

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query text")
    top_k: int = Field(2, ge=1, description="Number of top results to retrieve")
    file_ids: List[str] = Field(..., description="List of uploaded PDF file IDs")

class ContextChunk(BaseModel):
    file_id: str
    file_name: str
    page_number: int
    content: str

class QueryResponse(BaseModel):
    query: str
    context: List[ContextChunk]
    answer: str

@router.post("/query", response_model=QueryResponse)
def query_route(request: QueryRequest):
    """
    Handles document-based queries:
    - Validates input via Pydantic
    - Calls chat_service to get answer
    - Returns query, context, and answer
    """
    try:
        result = chat_service.handle_query(request.query, request.top_k, request.file_ids)
        return result
    except Exception as e:
        # Match test expectation: {"error": "..."} with status 500
        return JSONResponse(content={"error": str(e)}, status_code=500)
