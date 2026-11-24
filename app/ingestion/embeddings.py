"""
=============================================================================
TechNova AI Sales Assistant - Embedding Generation & ChromaDB Vector Store
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file Vector Database (ChromaDB) aur Embeddings Pipeline ko manage karti hai:
   1. `SentenceTransformer`: Local CPU-friendly `all-MiniLM-L6-v2` model se 384-dimensional dense vectors banata hai.
   2. `ChromaDB Client`: Persistent vector collection (`technova_knowledge`) manage karta hai.
   3. `store_documents()`: Documents aur embeddings ko ChromaDB mein upsert karta hai.
   4. `search_similar()`: Query ka cosine similarity vector search chalata hai.

🎯 USE CASE:
   - Data Ingestion ke waqt: Text ko vectors bana kar store karta hai.
   - Runtime Search ke waqt: User query ko vector bana kar similar chunks nikaalta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Embedding model badalna ho ya ChromaDB collection configuration tweak karni ho.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.ingestion.chunking import IngestedDocument


class EmbeddingManager:
    """Manages local CPU-friendly SentenceTransformer embeddings and ChromaDB operations."""
    
    _model_instance = None
    _chroma_client = None

    @classmethod
    def get_embedding_model(cls) -> SentenceTransformer:
        """Singleton pattern for embedding model to avoid reloading into RAM."""
        if cls._model_instance is None:
            print(f"[EmbeddingManager] Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
            cls._model_instance = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return cls._model_instance

    @classmethod
    def get_chroma_client(cls) -> chromadb.ClientAPI:
        """Initialize or return persistent ChromaDB client."""
        if cls._chroma_client is None:
            persist_path = Path(settings.CHROMA_PERSIST_DIR)
            persist_path.mkdir(parents=True, exist_ok=True)
            cls._chroma_client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        return cls._chroma_client

    @classmethod
    def get_collection(cls, collection_name: Optional[str] = None):
        """Retrieve or create a ChromaDB collection."""
        client = cls.get_chroma_client()
        name = collection_name or settings.CHROMA_COLLECTION_NAME
        return client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Compute 384-dimensional dense vectors for input texts."""
        model = cls.get_embedding_model()
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    @classmethod
    def store_documents(cls, documents: List[IngestedDocument], collection_name: Optional[str] = None) -> int:
        """Compute embeddings and upsert documents into ChromaDB."""
        if not documents:
            return 0

        collection = cls.get_collection(collection_name)
        
        ids = [doc.doc_id for doc in documents]
        texts = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        print(f"[EmbeddingManager] Generating embeddings for {len(texts)} document chunks...")
        embeddings = cls.generate_embeddings(texts)

        print(f"[EmbeddingManager] Upserting chunks into ChromaDB collection '{collection.name}'...")
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(ids)

    @classmethod
    def search_similar(
        cls,
        query: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Semantic search against the ChromaDB vector collection."""
        collection = cls.get_collection(collection_name)
        query_embedding = cls.generate_embeddings([query])[0]

        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = collection.query(**kwargs)

        retrieved: List[Dict[str, Any]] = []
        if results and results.get("ids") and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                retrieved.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": 1.0 - results["distances"][0][i]  # Cosine similarity
                })
        return retrieved
