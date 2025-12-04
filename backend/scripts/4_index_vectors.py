import json
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "../.env")
load_dotenv(dotenv_path=env_path)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
INPUT_FILE = os.path.join(script_dir, "../../data/gdpr_raw.json")
COLLECTION_NAME = "gdpr_articles"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    # Initialize Clients
    client = QdrantClient(url=QDRANT_URL)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Load Data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} articles.")

    # Re-create Collection
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created.")

    # Process and Index
    batch_size = 10
    total = len(data)
    
    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]
        print(f"Processing batch {i} to {min(i+batch_size, total)}...")
        
        texts = [item['text'] for item in batch]
        metadatas = [{"title": item['title'], "article_number": item['number'], "id": item['id']} for item in batch]
        ids = [i + idx for idx in range(len(batch))] # Simple integer IDs for Qdrant points

        try:
            # Generate Embeddings
            vectors = embeddings.embed_documents(texts)
            
            # Upsert to Qdrant
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=metadatas
                )
            )
        except Exception as e:
            print(f"Error indexing batch: {e}")

    print("Vector indexing complete.")

if __name__ == "__main__":
    main()
