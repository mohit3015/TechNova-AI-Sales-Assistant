"""
=============================================================================
TechNova AI Sales Assistant - ChromaDB Vector Knowledge Search
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file ChromaDB Vector Database se semantic information retrieve karti hai:
   1. `search_vector_knowledge()`: Query se match hone wale product suitability chunks dhoondhti hai.
   2. `search_policies_and_faqs()`: Company warranty, return rules, delivery time aur payment FAQs nikaalti hai.

🎯 USE CASE:
   Jab customer natural language mein sawaal poochta hai (e.g. "Python coding ke liye kaun sa achha hai" ya "Warranty kitni hai"),
   yeh file ChromaDB se cosine similarity ke basis par relevant context dhoondhti hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Vector search ke filters, top_k count ya document types customize karne hon.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from app.ingestion.embeddings import EmbeddingManager


def search_vector_knowledge(
    query: str,
    top_k: int = 5,
    doc_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Perform semantic similarity search on ChromaDB vector collection."""
    where_filter = None
    if doc_type:
        where_filter = {"doc_type": doc_type}

    results = EmbeddingManager.search_similar(
        query=query,
        top_k=top_k,
        where_filter=where_filter
    )
    return results


def search_policies_and_faqs(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve policies and FAQs relevant to customer questions."""
    all_results = EmbeddingManager.search_similar(query=query, top_k=top_k * 2)
    # Filter for policy or faq chunks
    policy_faq_results = [
        res for res in all_results
        if res.get("metadata", {}).get("doc_type") in ("company_policy", "faq")
    ]
    return policy_faq_results[:top_k]
