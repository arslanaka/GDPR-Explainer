from fastapi import APIRouter, HTTPException
from app.services.search_service import search_service

router = APIRouter()

@router.get("/search")
async def search_articles(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    results = search_service.search(q)
    return {"results": results}
