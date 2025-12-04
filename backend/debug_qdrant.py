from qdrant_client import QdrantClient
import sys

with open("debug_output.txt", "w") as f:
    try:
        client = QdrantClient(url="http://localhost:6333")
        f.write(f"Has search attribute: {hasattr(client, 'search')}\n")
        f.write(f"Has query attribute: {hasattr(client, 'query')}\n")
        f.write(f"Client dir: {dir(client)}\n")
    except Exception as e:
        f.write(f"Error initializing client: {e}\n")
