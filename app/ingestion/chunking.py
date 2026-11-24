"""
=============================================================================
TechNova AI Sales Assistant - Semantic Document Chunking Engine
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file raw product data, policies aur FAQs ko meaningful semantic chunks mein divide karti hai:
   1. `chunk_product_data()`: Har laptop ke liye 2 specific chunks banata hai:
      - Primary overview (specs, price, display, battery).
      - Suitability chunk (best for coding, ML, gaming).
   2. `chunk_policies_text()`: Policies ko section-wise split karke metadata attach karta hai.
   3. `chunk_faqs_json()`: Har question-answer pair ka vector document banata hai.

🎯 USE CASE:
   Data seeding ke waqt documents ko vector database mein store karne ke format (`IngestedDocument`) mein prepare karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Chunk size, overlap, ya metadata fields badalne ke liye.
=============================================================================
"""

import re
from typing import List, Dict, Any
from app.ingestion.cleaning import clean_text, sanitize_metadata_value


class IngestedDocument:
    """Standard document structure for vector database storage."""
    def __init__(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        self.doc_id = doc_id
        self.content = content
        self.metadata = {k: sanitize_metadata_value(v) for k, v in metadata.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata
        }


def chunk_product_data(products: List[Dict[str, Any]]) -> List[IngestedDocument]:
    """Convert structured product records into semantic documents for vector search."""
    documents: List[IngestedDocument] = []

    for p in products:
        pid = p["product_id"]
        
        # 1. Primary Recommendation Document (Semantic overview)
        primary_text = (
            f"Product Name: {p['name']} (Model ID: {pid})\n"
            f"Brand: {p['brand']} | Category: {p['category']}\n"
            f"Official Price: ₹{p['price']:,}\n"
            f"Processor: {p['processor']}\n"
            f"Memory (RAM): {p['ram_gb']}GB\n"
            f"Storage: {p['storage']}\n"
            f"Graphics (GPU): {p['gpu']}\n"
            f"Display: {p['display']}\n"
            f"Battery Life: {p['battery_life_hours']} Hours | Weight: {p['weight_kg']} kg\n"
            f"Best Suited For: {p['suitable_for']}\n"
            f"Detailed Description: {p['description']}\n"
            f"Warranty: {p['warranty_years']} Year(s) | Replacement: {p['return_days']} Days"
        )
        
        meta = {
            "doc_type": "product_overview",
            "product_id": pid,
            "name": p["name"],
            "category": p["category"],
            "ram_gb": p["ram_gb"],
            "price": p["price"],
            "stock_count": p["stock_count"]
        }
        documents.append(IngestedDocument(f"{pid}_overview", clean_text(primary_text), meta))

        # 2. Suitability & Use-case Chunk (Specialized for semantic queries like 'laptop for python, machine learning')
        suitability_text = (
            f"Laptop Recommendation: {p['name']} ({pid})\n"
            f"Target Users and Use Cases: {p['suitable_for']}.\n"
            f"Performance Profile: Powered by {p['processor']} with {p['ram_gb']}GB RAM and {p['gpu']}. "
            f"{p['description']}"
        )
        suitability_meta = {
            "doc_type": "product_suitability",
            "product_id": pid,
            "name": p["name"],
            "category": p["category"]
        }
        documents.append(IngestedDocument(f"{pid}_suitability", clean_text(suitability_text), suitability_meta))

    return documents


def chunk_policies_text(policy_text: str) -> List[IngestedDocument]:
    """Split company policies into section-based chunks with metadata."""
    documents: List[IngestedDocument] = []
    
    # Split by markdown headers like '## 1. Warranty...'
    sections = re.split(r"(?=##\s+\d+\.)", policy_text)
    
    for idx, sec in enumerate(sections):
        cleaned_sec = clean_text(sec)
        if not cleaned_sec:
            continue
        
        # Extract title from first line
        lines = cleaned_sec.split("\n")
        header = lines[0].replace("#", "").strip() if lines else f"Policy Section {idx + 1}"
        
        meta = {
            "doc_type": "company_policy",
            "section": header
        }
        documents.append(IngestedDocument(f"policy_sec_{idx + 1}", cleaned_sec, meta))

    return documents


def chunk_faqs_json(faqs: List[Dict[str, str]]) -> List[IngestedDocument]:
    """Convert customer FAQs into individual question-answer vector documents."""
    documents: List[IngestedDocument] = []

    for idx, faq in enumerate(faqs):
        q = faq.get("question", "").strip()
        a = faq.get("answer", "").strip()
        cat = faq.get("category", "General Assistance")
        
        content = (
            f"Category: {cat}\n"
            f"Frequently Asked Customer Question: {q}\n"
            f"TechNova Official Answer: {a}"
        )
        
        meta = {
            "doc_type": "faq",
            "category": cat,
            "question": q
        }
        documents.append(IngestedDocument(f"faq_{idx + 1}", clean_text(content), meta))

    return documents
