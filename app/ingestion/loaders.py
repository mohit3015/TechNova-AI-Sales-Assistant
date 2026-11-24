"""
=============================================================================
TechNova AI Sales Assistant - Document & Catalog Ingestion Loaders
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file raw data sources ko disk se load aur parse karne ka kaam karti hai:
   1. `load_products_csv()`: `data/products.csv` ko read karke types (int, float) cast karta hai.
   2. `load_policies_text()`: `data/policies.txt` ko clean text mein load karta hai.
   3. `load_faqs_json()`: `data/faqs.json` se questions & answers list nikaalta hai.

🎯 USE CASE:
   Database seeding script (`scripts/seed_db.py`) aur admin data updates ke time yeh loaders execute hote hain.

🛠️ WHEN TO MODIFY THIS FILE:
   - Naye data formats (e.g. PDF loader, Excel .xlsx loader) support karne ke liye.
=============================================================================
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from app.ingestion.cleaning import clean_text


def load_products_csv(file_path: Path | str) -> List[Dict[str, Any]]:
    """Load product catalog from CSV file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Product catalog not found at {path}")
    
    products = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned_row = {k.strip(): clean_text(v) if isinstance(v, str) else v for k, v in row.items()}
            # Cast numeric fields
            try:
                cleaned_row["price"] = int(float(cleaned_row.get("price", 0)))
                cleaned_row["ram_gb"] = int(cleaned_row.get("ram_gb", 0))
                cleaned_row["stock_count"] = int(cleaned_row.get("stock_count", 0))
                cleaned_row["warranty_years"] = int(cleaned_row.get("warranty_years", 1))
                cleaned_row["return_days"] = int(cleaned_row.get("return_days", 7))
                cleaned_row["battery_life_hours"] = float(cleaned_row.get("battery_life_hours", 0.0))
                cleaned_row["weight_kg"] = float(cleaned_row.get("weight_kg", 0.0))
            except (ValueError, TypeError):
                pass
            products.append(cleaned_row)
    return products


def load_policies_text(file_path: Path | str) -> str:
    """Load policy document from text or markdown file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policies document not found at {path}")
    
    with open(path, mode="r", encoding="utf-8") as f:
        content = f.read()
    return clean_text(content)


def load_faqs_json(file_path: Path | str) -> List[Dict[str, str]]:
    """Load company FAQs from JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"FAQs document not found at {path}")
    
    with open(path, mode="r", encoding="utf-8") as f:
        faqs = json.load(f)
    return faqs
