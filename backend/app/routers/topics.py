from fastapi import APIRouter, HTTPException
from app.services.graph_service import graph_service

router = APIRouter()

@router.get("/topics")
async def get_topics():
    topics = graph_service.get_all_topics()
    return {"topics": topics}

@router.get("/topics/{topic}")
async def get_articles_by_topic(topic: str):
    articles = graph_service.get_articles_by_topic(topic)
    if not articles:
        # It's possible the topic exists but has no articles (unlikely) or topic doesn't exist.
        # For now, return empty list or 404? Let's return empty list to be safe.
        return {"topic": topic, "articles": []}
    
    return {"topic": topic, "articles": articles}
