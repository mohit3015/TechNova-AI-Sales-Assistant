"""
=============================================================================
TechNova AI Sales Assistant - Global Application Configuration
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file poore project ki Central Configuration (Settings) handle karti hai.
   Isme Pydantic `BaseSettings` use kiya gaya hai jo `.env` file ko automatically
   read karke type-safe settings provide karta hai:
   - Database Paths (SQLite absolute path).
   - Vector DB Storage Path (ChromaDB absolute directory).
   - Model Names (SentenceTransformer & CrossEncoder).
   - LLM API Keys & Provider Settings (OpenRouter / Groq).

🎯 USE CASE:
   Har module (`connection.py`, `embeddings.py`, `generator.py`, `main.py`)
   `from app.config import settings` karke yahan se config values leta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Agar default database path, embedding model ya LLM parameters badalne hon.
   - Naya environment variable add karna ho.
=============================================================================
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_NAME: str = "TechNova AI Sales Assistant"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Paths (Always anchored to project root directory)
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    PRODUCTS_CSV_PATH: Path = BASE_DIR / "data" / "products.csv"
    POLICIES_PATH: Path = BASE_DIR / "data" / "policies.txt"
    FAQS_PATH: Path = BASE_DIR / "data" / "faqs.json"

    # Databases (Absolute paths to prevent CWD dependency)
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'technova_store.db'}"
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "technova_knowledge"

    # Embedding & Reranking Models
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 75
    TOP_K_RETRIEVAL: int = 5

    # LLM Settings
    LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "meta-llama/llama-3-8b-instruct:free"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **values):
        super().__init__(**values)
        # Ensure SQLite and ChromaDB paths are ALWAYS absolute project paths
        if self.DATABASE_URL.startswith("sqlite:///"):
            raw_path = self.DATABASE_URL.replace("sqlite:///", "")
            if not os.path.isabs(raw_path):
                clean_path = raw_path.lstrip("./\\")
                self.DATABASE_URL = f"sqlite:///{self.BASE_DIR / clean_path}"

        if not os.path.isabs(self.CHROMA_PERSIST_DIR):
            clean_chroma = self.CHROMA_PERSIST_DIR.lstrip("./\\")
            self.CHROMA_PERSIST_DIR = str(self.BASE_DIR / clean_chroma)

        # Strip any extraneous quotes from API keys
        if self.GROQ_API_KEY:
            self.GROQ_API_KEY = self.GROQ_API_KEY.strip("\"' ")
        if self.OPENROUTER_API_KEY:
            self.OPENROUTER_API_KEY = self.OPENROUTER_API_KEY.strip("\"' ")


settings = Settings()
