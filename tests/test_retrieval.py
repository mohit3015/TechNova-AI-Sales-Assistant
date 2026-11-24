"""
=============================================================================
TechNova AI Sales Assistant - Database & Vector Retrieval Test Suite
=============================================================================
📌 ROLE & PURPOSE:
   Yeh test suite Phase 1 ke Core Data Stores ko verify karta hai:
   1. SQLite Filtering: Hard constraints (Price <= ₹50k, RAM >= 16GB) check karta hai.
   2. ChromaDB Semantic Search: Vector similarity queries (e.g. "coding laptop") test karta hai.

🎯 USE CASE:
   Terminal se chala kar verify karein: `python tests/test_retrieval.py`.
=============================================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import SessionLocal
from app.database.crud import list_products, get_product_by_id
from app.ingestion.embeddings import EmbeddingManager


def test_sqlite_filtering():
    print("\n--- 1. Testing SQLite Filtering ---")
    db = SessionLocal()
    # Query: Laptops with at least 16GB RAM and under ₹50,000
    products = list_products(db, max_price=50000, min_ram=16)
    print(f"Products found with RAM >= 16GB & Price <= ₹50,000: {len(products)}")
    for p in products:
        print(f"  [ID: {p.product_id}] {p.name} | Price: ₹{p.price:,} | RAM: {p.ram_gb}GB | Stock: {p.stock_count}")
    db.close()
    assert len(products) > 0, "No products found matching SQL filters!"
    print(" SQL Filter Test: PASSED")


def test_chroma_semantic_search():
    print("\n--- 2. Testing ChromaDB Vector Semantic Search ---")
    query = "Mujhe coding aur machine learning ke liye laptop chahiye"
    print(f"Search Query: '{query}'")
    results = EmbeddingManager.search_similar(query=query, top_k=3)
    print(f"Retrieved {len(results)} relevant chunks from ChromaDB:")
    for i, res in enumerate(results, 1):
        doc_type = res['metadata'].get('doc_type', 'unknown')
        pid = res['metadata'].get('product_id', 'N/A')
        sim = res['similarity']
        print(f"  Top {i} (Similarity: {sim:.4f}) [Type: {doc_type}] [Product: {pid}]")
        snippet = res['content'][:140].replace('\n', ' ')
        print(f"    Snippet: {snippet}...")
    assert len(results) > 0, "No vector chunks retrieved from ChromaDB!"
    print(" ChromaDB Semantic Search Test: PASSED")


if __name__ == "__main__":
    test_sqlite_filtering()
    test_chroma_semantic_search()
    print("\n Phase 1 Verification 100% Successful! ")
