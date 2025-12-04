import os
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "gdpr_articles"

class SearchService:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def search(self, query: str, limit: int = 5):
        """
        Perform semantic search on GDPR articles.
        """
        try:
            vector = self.embeddings.embed_query(query)
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=vector,
                limit=limit,
                with_payload=True
            ).points
            
            return [
                {
                    "score": hit.score,
                    "article_number": hit.payload.get("article_number"),
                    "title": hit.payload.get("title"),
                    "id": hit.payload.get("id"),
                    "text_snippet": hit.payload.get("text")[:200] + "..." if hit.payload.get("text") else ""
                }
                for hit in results
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []

search_service = SearchService()
