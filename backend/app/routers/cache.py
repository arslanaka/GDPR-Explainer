from fastapi import APIRouter
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get Redis cache statistics.
    
    Returns:
        Cache statistics including hit rate, memory usage, and total keys
    """
    stats = cache_service.get_stats()
    return {
        "status": "success",
        "data": stats
    }


@router.post("/cache/invalidate/{pattern}")
async def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., 'chat:*', 'search:*')
    
    Returns:
        Number of keys invalidated
    """
    deleted_count = cache_service.invalidate_pattern(pattern)
    return {
        "status": "success",
        "message": f"Invalidated {deleted_count} cache entries",
        "deleted_count": deleted_count
    }


@router.delete("/cache/clear")
async def clear_all_cache():
    """
    Clear all cache entries.
    
    WARNING: This will delete all cached data.
    
    Returns:
        Confirmation message
    """
    deleted_count = cache_service.invalidate_pattern("*")
    return {
        "status": "success",
        "message": f"Cleared all cache ({deleted_count} entries)",
        "deleted_count": deleted_count
    }
