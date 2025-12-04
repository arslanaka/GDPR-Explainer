from fastapi import APIRouter, HTTPException
from app.services.explainer_service import explainer_service

router = APIRouter()

@router.get("/explain/{article_id}")
async def explain_article(article_id: str):
    # Ensure ID format
    if not article_id.startswith("ART-"):
        article_id = f"ART-{article_id}"
        
    result = explainer_service.explain_article(article_id)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return result
