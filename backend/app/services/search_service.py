import os
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.services.llm_factory import get_embeddings
from app.services.cache_service import cache_service
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "gdpr_articles"

class SearchService:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.embeddings = get_embeddings() # Changed from OpenAIEmbeddings to get_embeddings()
        self.collection_name = COLLECTION_NAME # Added collection_name as instance variable

    def search(self, query: str, limit: int = 5, language: str = "en"):
        """
        Semantic search with Redis caching.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            language: Language code (for future multi-language support)
        
        Returns:
            List of search results
        """
        # Check cache first
        cache_key_params = {"limit": limit, "lang": language}
        cached_results = cache_service.get("search", query, **cache_key_params)
        
        if cached_results:
            logger.info(f"✅ Cache hit for search: {query[:50]}...")
            return cached_results
        
        # Cache miss - perform vector search
        logger.info(f"❌ Cache miss for search: {query[:50]}...")
        
        try:
            # Generate query embedding
            query_vector = self.embeddings.embed_query(query)
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True # Ensure payload is returned for formatting
            )
            
            # Format results
            formatted_results = [
                {
                    "id": hit.payload.get("id"),
                    "article_number": hit.payload.get("article_number"),
                    "title": hit.payload.get("title"),
                    "text_snippet": hit.payload.get("text", "")[:300] + "...",
                    "score": hit.score
                }
                for hit in results
            ]
            
            # Cache results
            cache_service.set("search", query, formatted_results, **cache_key_params)
            logger.info(f"💾 Cached search results for: {query[:50]}...")
            
            return formatted_results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

search_service = SearchService()
