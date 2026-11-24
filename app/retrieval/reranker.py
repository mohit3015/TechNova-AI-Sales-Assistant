"""
=============================================================================
TechNova AI Sales Assistant - Cross-Encoder Reranker
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file retrieved candidates ki ranking accuracy improve karti hai.
   Isme `cross-encoder/ms-marco-MiniLM-L-6-v2` model use hota hai jo query aur candidate laptop
   ke beech direct deep semantic interaction score compute karta hai aur best laptop ko top par rank karta hai.

🎯 USE CASE:
   SQL database se mile candidate laptops ko customer ke query ("web dev", "machine learning", "gaming")
   ke relevance ke hisaab se reorder karne ke liye.

🛠️ WHEN TO MODIFY THIS FILE:
   - Reranker model change karna ho ya reranking thresholds adjust karne hon.
=============================================================================
"""

from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder
from app.config import settings


class CrossEncoderReranker:
    """Reranker using Cross-Encoder model to compute deep query-document interaction scores."""
    
    _reranker_instance = None

    @classmethod
    def get_model(cls) -> CrossEncoder:
        if cls._reranker_instance is None:
            try:
                print(f"[Reranker] Loading CrossEncoder model: {settings.RERANKER_MODEL}...")
                cls._reranker_instance = CrossEncoder(settings.RERANKER_MODEL)
            except Exception as e:
                print(f"[Reranker] Warning: Could not load CrossEncoder ({e}). Fallback to semantic ranking.")
                cls._reranker_instance = False
        return cls._reranker_instance

    @classmethod
    def rerank(
        cls,
        query: str,
        candidates: List[Dict[str, Any]],
        text_key: str = "search_text",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Reranks candidates using the Cross-Encoder.
        Each candidate dict must contain `text_key` which has the product text.
        """
        if not candidates:
            return []

        model = cls.get_model()
        if not model:
            # Fallback if model could not be initialized
            return candidates[:top_k]

        pairs: List[Tuple[str, str]] = []
        for c in candidates:
            text = c.get(text_key, "")
            pairs.append((query, text))

        try:
            scores = model.predict(pairs, show_progress_bar=False)
            for idx, candidate in enumerate(candidates):
                candidate["rerank_score"] = float(scores[idx])

            # Sort by rerank_score descending
            ranked = sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            return ranked[:top_k]
        except Exception as e:
            print(f"[Reranker] Error during reranking: {e}")
            return candidates[:top_k]
