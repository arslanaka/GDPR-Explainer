# GDPR Explainer - Backend API

> **Note:** This is the backend repository. For the frontend, see [GDPR-Explainer-UI](https://github.com/arslanaka/GDPR-Explainer-UI-.git)

GDPR Explainer Backend is an intelligent API that powers AI-driven GDPR compliance assistance. Built with FastAPI, it combines Retrieval-Augmented Generation (RAG), Neo4j Graph Database, Qdrant Vector Search, and Redis caching to deliver accurate, context-aware explanations of GDPR regulations.

## 🚀 Features

- **🤖 AI-Powered Chat API:** Streaming responses with LangChain and OpenAI/Gemini
- **📊 Knowledge Graph:** Neo4j-based relationship mapping between GDPR articles
- **🔍 Semantic Search:** Qdrant vector search for intelligent article discovery
- **⚡ Redis Caching:** 60-70% cost reduction with intelligent response caching
- **🌍 Multi-language Support:** Ready for German/English bilingual responses
- **📈 Monitoring APIs:** Cache statistics and performance metrics

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Backend            │
│  ┌──────────────────────────┐  │
│  │   Chat Service (RAG)     │  │
│  │   - Router               │  │
│  │   - QA Chain             │  │
│  │   - Streaming Response   │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │   Cache Service          │  │
│  │   - Redis Pool           │  │
│  │   - TTL Management       │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
       │         │         │
       ▼         ▼         ▼
   ┌─────┐  ┌──────┐  ┌────────┐
   │Neo4j│  │Qdrant│  │ Redis  │
   └─────┘  └──────┘  └────────┘
```

## 🛠️ Tech Stack

- **API Framework:** [FastAPI](https://fastapi.tiangolo.com/) - High-performance async API
- **AI/LLM:** [LangChain](https://python.langchain.com/) - LLM orchestration
- **Graph Database:** [Neo4j](https://neo4j.com/) - GDPR article relationships
- **Vector Database:** [Qdrant](https://qdrant.tech/) - Semantic search
- **Cache:** [Redis](https://redis.io/) - Response caching (70% cost reduction)
- **LLM Providers:** OpenAI GPT-4 / Google Gemini

## 📋 Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Python 3.10+](https://www.python.org/)
- OpenAI API Key or Google API Key

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/arslanaka/GDPR-Explainer.git
cd GDPR-Explainer
```

### 2. Start Infrastructure

Start Neo4j, Qdrant, and Redis using Docker Compose:

```bash
docker-compose up -d
```

**Services:**
- Neo4j: `http://localhost:7474` (Browser), `bolt://localhost:7687` (Bolt)
- Qdrant: `http://localhost:6333`
- Redis: `localhost:6379`

### 3. Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

Create a `.env` file in the root directory:

```env
# LLM Provider (choose one)
OPENAI_API_KEY=your_openai_key_here
# or
GOOGLE_API_KEY=your_google_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50

# Cache TTL (in seconds)
CACHE_TTL_CHAT=3600        # 1 hour
CACHE_TTL_SEARCH=7200      # 2 hours
CACHE_TTL_ARTICLE=86400    # 24 hours
CACHE_TTL_EXPLANATION=43200 # 12 hours
```

### 5. Data Pipeline (First Time Setup)

Run the data ingestion scripts to populate databases:

```bash
# Parse GDPR text
python scripts/1_parse_gdpr.py

# Extract graph relationships
python scripts/2_extract_graph.py

# Load data into Neo4j
python scripts/3_load_neo4j.py

# Index vectors in Qdrant
python scripts/4_index_vectors.py
```

### 6. Run the API

```bash
uvicorn main:app --reload
```

**API Endpoints:**
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/`
- Chat: `POST http://localhost:8000/api/chat`
- Search: `GET http://localhost:8000/api/search?q=encryption`
- Cache Stats: `GET http://localhost:8000/api/cache/stats`

## 📚 API Documentation

### Chat Endpoint

**POST** `/api/chat`

```json
{
  "query": "What is Article 5 about?",
  "model": "openai",
  "language": "en"
}
```

**Response:** Streaming NDJSON

```json
{"type": "sources", "results": [...]}
{"type": "token", "content": "Article"}
{"type": "token", "content": " 5"}
...
```

### Search Endpoint

**GET** `/api/search?q=data+protection&limit=5`

**Response:**
```json
{
  "results": [
    {
      "id": "ART-5",
      "article_number": 5,
      "title": "Principles relating to processing of personal data",
      "text_snippet": "...",
      "score": 0.89
    }
  ]
}
```

### Cache Statistics

**GET** `/api/cache/stats`

**Response:**
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "total_keys": 1234,
    "hits": 5678,
    "misses": 1234,
    "hit_rate": 82.15,
    "memory_used_mb": 45.23
  }
}
```

## 🚀 Performance

### Redis Caching Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Response Time (cached) | 2-5s | 50-200ms | **10-25x faster** |
| LLM API Calls | 100% | 30-40% | **60-70% reduction** |
| Cost per 1000 queries | $50 | $15-20 | **60-70% savings** |
| Concurrent Users | 10-20 | 50-100 | **5x scalability** |

See [docs/CACHING.md](docs/CACHING.md) for detailed caching documentation.

## 📁 Project Structure

```
backend/
├── app/
│   ├── routers/          # API endpoints
│   │   ├── chat.py       # Chat streaming
│   │   ├── search.py     # Semantic search
│   │   ├── articles.py   # Article details
│   │   ├── explain.py    # Article explanations
│   │   ├── topics.py     # Topic browsing
│   │   └── cache.py      # Cache management
│   └── services/         # Business logic
│       ├── cache_service.py      # Redis caching
│       ├── chat_service.py       # RAG pipeline
│       ├── search_service.py     # Vector search
│       ├── graph_service.py      # Neo4j queries
│       ├── explainer_service.py  # LLM explanations
│       └── llm_factory.py        # LLM initialization
├── scripts/              # Data ingestion
│   ├── 1_parse_gdpr.py
│   ├── 2_extract_graph.py
│   ├── 3_load_neo4j.py
│   └── 4_index_vectors.py
├── docs/                 # Documentation
│   └── CACHING.md
├── main.py              # FastAPI app
├── requirements.txt     # Dependencies
└── docker-compose.yml   # Infrastructure
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test cache functionality
curl http://localhost:8000/api/cache/stats

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is GDPR?", "model": "openai"}'
```

## 🔧 Development

### Adding New Endpoints

1. Create router in `app/routers/`
2. Add service logic in `app/services/`
3. Register router in `main.py`

### Invalidating Cache

```bash
# Invalidate all chat cache
curl -X POST http://localhost:8000/api/cache/invalidate/chat:*

# Clear all cache
curl -X DELETE http://localhost:8000/api/cache/clear
```

## 🌍 Deployment

### Docker Production Build

```bash
# Build production image
docker build -t gdpr-explainer-backend .

# Run container
docker run -p 8000:8000 --env-file .env gdpr-explainer-backend
```

### Environment Variables for Production

- Use managed Redis (AWS ElastiCache, Redis Cloud)
- Enable Redis persistence (RDB + AOF)
- Set up monitoring (CloudWatch, Datadog)
- Use secrets manager for API keys

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Repositories

- **Frontend:** [GDPR-Explainer-UI](https://github.com/arslanaka/GDPR-Explainer-UI-.git)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check [docs/CACHING.md](docs/CACHING.md) for caching troubleshooting

---

**Built with ❤️ for GDPR compliance**
