from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GDPR Explainer API is running"}

def test_search_articles():
    # Test with a common term
    response = client.get("/api/search?q=security")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    # Check structure
    assert "article_number" in data["results"][0]

def test_get_article_details():
    # Assuming Article 32 exists (it should)
    response = client.get("/api/articles/ART-32")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 32
    assert "obligations" in data

def test_get_topics():
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert isinstance(data["topics"], list)

def test_chat_general():
    # Test the chat endpoint with a general question
    payload = {"query": "What is personal data?"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] in ["answer", "search_results"]
    assert "content" in data

def test_chat_explain_intent():
    # Test routing to explanation
    payload = {"query": "Explain Article 5"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    # It might route to explanation or answer depending on LLM, but usually explanation
    if data["type"] == "explanation":
        assert "related_data" in data
