"""
=============================================================================
TechNova AI Sales Assistant - One-Command Database Seeding & Ingestion
=============================================================================
📌 ROLE & PURPOSE:
   Yeh hamara Master Ingestion Script hai jo poore project ka initial data load karta hai:
   1. SQLite Database initialize karta hai aur `data/products.csv` ke 12 laptops insert karta hai.
   2. Products, Policies (`policies.txt`), aur FAQs (`faqs.json`) ke 39 semantic chunks banata hai.
   3. `all-MiniLM-L6-v2` se embeddings compute karke ChromaDB vector store mein index karta hai.

🎯 USE CASE:
   Terminal se ek command chala kar databases initialize karne ke liye:
   `python scripts/seed_db.py`

🛠️ WHEN TO MODIFY OR RUN THIS FILE:
   - Jab bhi `data/products.csv`, `policies.txt` ya `faqs.json` mein koi naya data add/edit karein,
     is script ko dobara run karein taaki SQLite aur ChromaDB sync ho jayein.
=============================================================================
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.database.connection import init_db, SessionLocal
from app.database.crud import upsert_product
from app.ingestion.loaders import load_products_csv, load_policies_text, load_faqs_json
from app.ingestion.chunking import chunk_product_data, chunk_policies_text, chunk_faqs_json
from app.ingestion.embeddings import EmbeddingManager


def run_seeding():
    print("=" * 60)
    print(" TechNova AI Sales Assistant - Database Seeding & Ingestion ")
    print("=" * 60)

    # 1. Initialize SQLite Database
    print("\n[1/4] Initializing SQLite database...")
    init_db()
    db = SessionLocal()

    # 2. Ingest Products into SQLite (Authoritative Source for Price & Stock)
    print(f"\n[2/4] Loading product records from {settings.PRODUCTS_CSV_PATH}...")
    products = load_products_csv(settings.PRODUCTS_CSV_PATH)
    print(f" -> Found {len(products)} products in catalog.")

    for p in products:
        upsert_product(db, p)
    db.close()
    print(f" -> Successfully inserted/updated {len(products)} products in SQLite.")

    # 3. Prepare Chunks for Vector Store (ChromaDB)
    print("\n[3/4] Preparing semantic chunks for vector database...")
    all_chunks = []

    # Product overview & suitability chunks
    product_chunks = chunk_product_data(products)
    all_chunks.extend(product_chunks)
    print(f" -> Generated {len(product_chunks)} product knowledge chunks.")

    # Policies
    if settings.POLICIES_PATH.exists():
        policies_text = load_policies_text(settings.POLICIES_PATH)
        policy_chunks = chunk_policies_text(policies_text)
        all_chunks.extend(policy_chunks)
        print(f" -> Generated {len(policy_chunks)} policy chunks.")

    # FAQs
    if settings.FAQS_PATH.exists():
        faqs = load_faqs_json(settings.FAQS_PATH)
        faq_chunks = chunk_faqs_json(faqs)
        all_chunks.extend(faq_chunks)
        print(f" -> Generated {len(faq_chunks)} FAQ chunks.")

    # 4. Generate Embeddings & Upsert to ChromaDB
    print(f"\n[4/4] Ingesting {len(all_chunks)} total chunks into ChromaDB '{settings.CHROMA_COLLECTION_NAME}'...")
    count = EmbeddingManager.store_documents(all_chunks)

    print("\n" + "=" * 60)
    print(" Seeding Completed Successfully! ")
    print(f"  • SQLite Products Table: {len(products)} laptops")
    print(f"  • ChromaDB Collection:   {count} vector documents indexed")
    print("=" * 60)


if __name__ == "__main__":
    run_seeding()
