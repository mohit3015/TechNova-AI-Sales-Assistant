"""
=============================================================================
TechNova AI Sales Assistant - Deterministic SQL Search & Fallbacks
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file Relational Database (SQLite) par deterministic queries chalati hai:
   1. `search_products_sql()`: Live database se laptops filter karta hai.
   2. `get_alternative_products()`: Zero-match scenario mein smart sales upselling aur downselling options find karta hai.

🎯 USE CASE:
   Hybrid retrieval pipeline ka first phase yeh file handle karti hai taaki hallucinated price/stock eliminate ho sake.

🛠️ WHEN TO MODIFY THIS FILE:
   - Budget filtering logic ya alternative recommendation strategy change karni ho.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import crud
from app.database.models import Product


def search_products_sql(
    db: Session,
    max_price: Optional[int] = None,
    min_ram: Optional[int] = None,
    brand: Optional[str] = None,
    product_ids: Optional[List[str]] = None,
    in_stock_only: bool = True,
    sort_by_price_desc: bool = False,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Query authoritative SQL database for products meeting hard criteria."""
    products: List[Product] = crud.list_products(
        db=db,
        max_price=max_price,
        min_ram=min_ram,
        brand=brand,
        product_ids=product_ids,
        in_stock_only=in_stock_only,
        sort_by_price_desc=sort_by_price_desc,
        limit=limit
    )
    return [p.to_dict() for p in products]


def get_alternative_products(
    db: Session,
    max_price: Optional[int] = None,
    min_ram: Optional[int] = None,
    limit: int = 3
) -> Dict[str, Any]:
    """Smart sales fallback when 0 products match the customer's strict constraints.
    Finds:
    1. Laptops with the desired RAM at the nearest starting price above budget (upsell).
    2. Laptops within the customer's budget with lower RAM (downsell/alternative).
    """
    alternatives = {
        "higher_budget_options": [],
        "budget_friendly_options": []
    }

    # 1. If RAM requested was specified, find nearest price matching that RAM
    if min_ram:
        higher_price_prods = (
            db.query(Product)
            .filter(Product.ram_gb >= min_ram, Product.stock_count > 0)
            .order_by(Product.price.asc())
            .limit(limit)
            .all()
        )
        alternatives["higher_budget_options"] = [p.to_dict() for p in higher_price_prods]

    # 2. If budget was specified, find best available laptops within that budget
    if max_price:
        in_budget_prods = (
            db.query(Product)
            .filter(Product.price <= max_price, Product.stock_count > 0)
            .order_by(Product.price.desc())
            .limit(limit)
            .all()
        )
        alternatives["budget_friendly_options"] = [p.to_dict() for p in in_budget_prods]

    return alternatives
