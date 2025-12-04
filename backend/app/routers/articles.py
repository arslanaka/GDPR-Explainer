from fastapi import APIRouter, HTTPException
from app.services.graph_service import graph_service

router = APIRouter()

@router.get("/articles/{article_id}")
async def get_article(article_id: str):
    # Ensure ID format (e.g., "ART-1")
    if not article_id.startswith("ART-"):
        # Try to fix if user sends just "1"
        article_id = f"ART-{article_id}"
        
    data = graph_service.get_article_details(article_id)
    if not data:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return data
