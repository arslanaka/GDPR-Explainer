# GDPR Explainer

GDPR Explainer is an intelligent, AI-powered application designed to help users understand and navigate the General Data Protection Regulation (GDPR). By leveraging Retrieval-Augmented Generation (RAG), Graph Databases, and Vector Search, it provides accurate, context-aware explanations and visualizations of complex legal concepts.

## 🚀 Features

- **AI-Powered Chat:** Ask questions about GDPR and get accurate answers backed by the official regulation text.
- **Knowledge Graph Visualization:** Explore the relationships between different GDPR articles, recitals, and key concepts using an interactive graph.
- **Semantic Search:** Find relevant articles and topics not just by keywords, but by meaning.
- **RAG Architecture:** Combines the power of Large Language Models (LLMs) with structured (Graph) and unstructured (Vector) data for high-fidelity responses.

## 🛠️ Tech Stack

### Frontend
- **Framework:** [Next.js 16](https://nextjs.org/) (React 19)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Visualization:** [Cytoscape.js](https://js.cytoscape.org/) for graph rendering
- **Animations:** [Framer Motion](https://www.framer.com/motion/)

### Backend
- **API:** [FastAPI](https://fastapi.tiangolo.com/)
- **AI/LLM Orchestration:** [LangChain](https://python.langchain.com/)
- **Graph Database:** [Neo4j](https://neo4j.com/)
- **Vector Database:** [Qdrant](https://qdrant.tech/)
- **LLM Providers:** OpenAI / Google Gemini

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- [Docker](https://www.docker.com/) & Docker Compose (for the databases)
- [Python 3.10+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)

## ⚡ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/arslanaka/GDPR-Explainer.git
cd GDPR-Explainer
```

### 2. Start Infrastructure (Databases)

Start Neo4j and Qdrant using Docker Compose:

```bash
docker-compose up -d
```

### 3. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Configuration:**
Create a `.env` file in the `backend` directory with your API keys and database credentials:

```env
OPENAI_API_KEY=your_openai_key_here
# or
GOOGLE_API_KEY=your_google_api_key_here

# Neo4j Configuration (Default from docker-compose)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
```

### 4. Data Pipeline (Ingestion)

Run the scripts to parse GDPR text, build the graph, and index vectors. **Note:** Ensure your databases are running.

```bash
# From the backend directory
python scripts/1_parse_gdpr.py
python scripts/2_extract_graph.py
python scripts/3_load_neo4j.py
python scripts/4_index_vectors.py
```

### 5. Run the Backend

```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`. You can view the docs at `http://localhost:8000/docs`.

### 6. Frontend Setup

Open a new terminal, navigate to the frontend directory, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
