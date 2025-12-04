from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search, articles, explain, topics, chat

app = FastAPI(title="GDPR Explainer API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(articles.router, prefix="/api", tags=["Articles"])
app.include_router(explain.router, prefix="/api", tags=["Explain"])
app.include_router(topics.router, prefix="/api", tags=["Topics"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "GDPR Explainer API is running"}
