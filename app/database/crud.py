"""
=============================================================================
TechNova AI Sales Assistant - Database CRUD Operations (Safe SQL Queries)
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file database ke saare Create, Read, Update, Delete (CRUD) operations handle karti hai.
   Isme:
   1. `list_products()`: Safe parameterized product filtering (budget, RAM, brand, stock).
   2. `get_product_by_id()`: Exact product lookup.
   3. `create_lead()`: Customer details ko `leads` table mein save karna.
   4. `add_chat_message()` & `get_recent_chat_history()`: Multi-turn session memory persist karna.

🎯 USE CASE:
   LLM ko direct raw SQL execute karne ki permission nahi hai; balki yeh file safe ORM queries run karti hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Nayi custom database query ya sorting criteria add karna ho.
=============================================================================
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import Product, Lead, ChatHistory


# --- Product Operations ---

def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
    return db.query(Product).filter(Product.product_id == product_id).first()


def list_products(
    db: Session,
    max_price: Optional[int] = None,
    min_ram: Optional[int] = None,
    brand: Optional[str] = None,
    product_ids: Optional[List[str]] = None,
    in_stock_only: bool = True,
    sort_by_price_desc: bool = False,
    limit: int = 10
) -> List[Product]:
    """Safe, parameterized product filtering with SQLAlchemy."""
    query = db.query(Product)

    if product_ids:
        query = query.filter(Product.product_id.in_(product_ids))
    if in_stock_only:
        query = query.filter(Product.stock_count > 0)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if min_ram is not None:
        query = query.filter(Product.ram_gb >= min_ram)
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    # Sort by price ascending or descending based on preference
    if sort_by_price_desc:
        return query.order_by(Product.price.desc()).limit(limit).all()
    return query.order_by(Product.price.asc()).limit(limit).all()


def upsert_product(db: Session, product_data: Dict[str, Any]) -> Product:
    pid = product_data.get("product_id")
    existing = db.query(Product).filter(Product.product_id == pid).first()
    
    if existing:
        for k, v in product_data.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_prod = Product(**product_data)
        db.add(new_prod)
        db.commit()
        db.refresh(new_prod)
        return new_prod


# --- Lead Operations ---

def create_lead(db: Session, lead_data: Dict[str, Any]) -> Lead:
    lead = Lead(**lead_data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_leads(db: Session, limit: int = 20) -> List[Lead]:
    return db.query(Lead).order_by(desc(Lead.created_at)).limit(limit).all()


# --- Chat History Operations ---

def add_chat_message(db: Session, session_id: str, role: str, content: str) -> ChatHistory:
    msg = ChatHistory(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_recent_chat_history(db: Session, session_id: str, limit: int = 6) -> List[ChatHistory]:
    msgs = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(desc(ChatHistory.created_at)).limit(limit).all()
    return list(reversed(msgs))
