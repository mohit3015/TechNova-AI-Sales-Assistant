"""
=============================================================================
TechNova AI Sales Assistant - Main FastAPI Server Application
=============================================================================
📌 ROLE & PURPOSE:
   Yeh hamare project ka Core Backend Web Server (FastAPI Entry Point) hai.
   Isme:
   1. Lifespan Handler: Server start hote hi SQLite tables aur ChromaDB initialize karta hai.
   2. CORS Middleware: Streamlit frontend (localhost:8501) ko API access karne ki permission deta hai.
   3. API Routers: `/api/products`, `/api/leads`, aur `/api/chat` ko register karta hai.
   4. Health Monitoring: `/health` endpoint jo SQLite aur ChromaDB ki live health report karta hai.

🎯 USE CASE:
   Jab terminal mein `uvicorn app.main:app --reload` chalta hai, yeh file execute hoti hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Naye API routers add karne hon.
   - Server startup/shutdown logic ya CORS security policies change karni hon.
=============================================================================
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database.connection import init_db, get_db
from app.ingestion.embeddings import EmbeddingManager
from app.api.products import router as products_router
from app.api.leads import router as leads_router
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables and Chroma collections are initialized
    print(f"[{settings.APP_NAME}] Starting up in {settings.APP_ENV} mode...")
    print(f"[{settings.APP_NAME}] Database path: {settings.DATABASE_URL}")
    print(f"[{settings.APP_NAME}] ChromaDB path: {settings.CHROMA_PERSIST_DIR}")
    init_db()
    try:
        EmbeddingManager.get_collection()
        print(f"[{settings.APP_NAME}] Connected to ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}'")
    except Exception as e:
        print(f"[{settings.APP_NAME}] ChromaDB connection warning: {e}")
    yield
    print(f"[{settings.APP_NAME}] Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Sales Assistant & Intelligent Product Recommendation API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (Restricted to verified frontends, preventing wildcard exposure)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Include API Routers
app.include_router(products_router, prefix="/api")
app.include_router(leads_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/", tags=["Root"])
def root_status():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint verifying SQLite and ChromaDB availability."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    chroma_status = "healthy"
    try:
        col = EmbeddingManager.get_collection()
        count = col.count()
    except Exception as e:
        chroma_status = f"unhealthy: {e}"
        count = 0

    return {
        "status": "healthy" if db_status == "healthy" and chroma_status == "healthy" else "degraded",
        "database": {
            "status": db_status
        },
        "vector_database": {
            "status": chroma_status,
            "indexed_chunks": count
        }
    }
