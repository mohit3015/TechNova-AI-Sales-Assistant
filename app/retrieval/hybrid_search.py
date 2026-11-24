"""
=============================================================================
TechNova AI Sales Assistant - Hybrid Retrieval Engine (Core RAG Orchestrator)
=============================================================================
📌 ROLE & PURPOSE:
   Yeh project ka Core RAG Orchestrator hai jo 2 alag-alag search systems ko combine karta hai:
   1. SQL Search: Exact constraints enforce karta hai (Price <= Budget, RAM >= 16GB, Stock > 0).
   2. Vector Search: ChromaDB se product suitability, policies aur FAQs retrieve karta hai.
   3. Cross-Encoder Reranker: SQL-approved candidate laptops ko customer query ke semantic match par rank karta hai.
   4. Smart Fallback: Agar budget ke andar koi laptop na mile, toh nearest alternatives provide karta hai.

🎯 USE CASE:
   `sales_agent.py` customer ki recommendation query par isko call karke grounded context leta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Retrieval workflow, candidate merging, ya top_k recommendations count change karne ke liye.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.retrieval.sql_search import search_products_sql, get_alternative_products
from app.retrieval.vector_search import search_vector_knowledge, search_policies_and_faqs
from app.retrieval.reranker import CrossEncoderReranker


class HybridRetriever:
    """Orchestrates Hybrid Search combining SQL deterministic constraints with ChromaDB vector semantics."""

    @classmethod
    def search(
        cls,
        db: Session,
        query: str,
        max_price: Optional[int] = None,
        min_ram: Optional[int] = None,
        brand: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Perform Hybrid Search:
        1. SQL candidate search with strict filters.
        2. Vector search for semantic understanding + policy/FAQ context.
        3. Candidate reranking via Cross-Encoder.
        4. Zero-match alternative suggestions if SQL yields 0 results.
        """
        # 1. SQL Search (Authoritative for pricing, stock, hardware)
        lower_q = query.lower()
        sort_desc = any(w in lower_q for w in [
            "highest", "mehenga", "mahanga", "expensive", "costliest", "premium",
            "top price", "top model", "sabse mehenga", "sabse mahanga"
        ]) or (max_price is not None and max_price >= 90000)
        
        sql_products = search_products_sql(
            db=db,
            max_price=max_price,
            min_ram=min_ram,
            brand=brand,
            in_stock_only=True,
            sort_by_price_desc=sort_desc,
            limit=10
        )

        alternatives = None
        # Handle zero-result scenario for smart sales guidance
        if not sql_products and (max_price or min_ram):
            alternatives = get_alternative_products(
                db=db,
                max_price=max_price,
                min_ram=min_ram,
                limit=3
            )

        # 2. Vector Search for relevant contextual knowledge (Policies & FAQs)
        policy_faq_chunks = search_policies_and_faqs(query=query, top_k=2)

        # 3. Vector Search for product suitability context
        vector_product_chunks = search_vector_knowledge(
            query=query,
            top_k=5,
            doc_type="product_suitability"
        )
        suitability_map = {
            chunk["metadata"].get("product_id"): chunk["content"]
            for chunk in vector_product_chunks
            if chunk.get("metadata", {}).get("product_id")
        }

        # 4. Prepare candidate representations for reranking
        candidates = []
        for p in sql_products:
            pid = p["product_id"]
            suitability_info = suitability_map.get(pid, p["suitable_for"])
            
            # Text representation evaluated by Cross-Encoder
            search_text = (
                f"Product: {p['name']} (ID: {pid})\n"
                f"Processor: {p['processor']} | RAM: {p['ram_gb']}GB | GPU: {p['gpu']}\n"
                f"Price: ₹{p['price']:,}\n"
                f"Suitable For: {suitability_info}\n"
                f"Description: {p['description']}"
            )
            candidates.append({
                "product": p,
                "search_text": search_text,
                "suitability_snippet": suitability_info
            })

        # 5. Cross-Encoder Reranking
        ranked_candidates = CrossEncoderReranker.rerank(
            query=query,
            candidates=candidates,
            text_key="search_text",
            top_k=top_k
        )

        # 6. Format final structured result
        recommended_products = []
        sources = []

        for c in ranked_candidates:
            prod = c["product"]
            recommended_products.append({
                "product_id": prod["product_id"],
                "name": prod["name"],
                "price": prod["price"],
                "ram_gb": prod["ram_gb"],
                "processor": prod["processor"],
                "storage": prod["storage"],
                "gpu": prod["gpu"],
                "display": prod["display"],
                "stock_count": prod["stock_count"],
                "warranty_years": prod["warranty_years"],
                "return_days": prod["return_days"],
                "suitable_for": prod["suitable_for"],
                "rerank_score": c.get("rerank_score", 0.0),
                "suitability_reason": c.get("suitability_snippet", "")
            })
            sources.append(f"product_catalog_{prod['product_id']}")

        for pf in policy_faq_chunks:
            sources.append(pf.get("id", "policy_faq_doc"))

        return {
            "query": query,
            "filters_applied": {
                "max_price": max_price,
                "min_ram": min_ram,
                "brand": brand
            },
            "products_found_count": len(recommended_products),
            "recommended_products": recommended_products,
            "policy_and_faq_context": [
                {
                    "id": pf["id"],
                    "content": pf["content"],
                    "metadata": pf["metadata"]
                }
                for pf in policy_faq_chunks
            ],
            "alternatives": alternatives,
            "sources": sources
        }
