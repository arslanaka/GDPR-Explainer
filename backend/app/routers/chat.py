from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.services.chat_service import chat_service

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    model: Optional[str] = "openai" # "openai" or "gemini"

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    return StreamingResponse(
        chat_service.chat_stream(request.query, model_provider=request.model),
        media_type="application/x-ndjson"
    )
