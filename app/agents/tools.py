"""
=============================================================================
TechNova AI Sales Assistant - Agent Execution Tools
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file Sales Agent ke liye individual tools (functions) provide karti hai:
   1. `search_catalog_tool()`: Hybrid Search call karta hai.
   2. `compare_products_tool()`: 2-4 laptops ki specifications fetch karta hai.
   3. `search_policy_faq_tool()`: Company policies aur FAQs dhoondhta hai.
   4. `capture_lead_tool()`: Lead ko database mein store karta hai.
   5. `get_conversation_history_tool()`: Session history load karta hai.

🎯 USE CASE:
   Sales Agent inhi functions ko as discrete tools execute karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Agent ke liye naya tool (e.g. order tracking, pincode serviceability check) add karna ho.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database import crud
from app.retrieval.hybrid_search import HybridRetriever
from app.retrieval.vector_search import search_policies_and_faqs


def search_catalog_tool(
    db: Session,
    query: str,
    max_price: Optional[int] = None,
    min_ram: Optional[int] = None,
    brand: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """Tool: Hybrid Search over SQLite product database and ChromaDB knowledge base."""
    return HybridRetriever.search(
        db=db,
        query=query,
        max_price=max_price,
        min_ram=min_ram,
        brand=brand,
        top_k=top_k
    )


def compare_products_tool(db: Session, product_ids: List[str]) -> Dict[str, Any]:
    """Tool: Retrieve full hardware specifications of multiple laptops for comparison."""
    products = []
    for pid in product_ids:
        p = crud.get_product_by_id(db, pid.strip().upper())
        if p:
            products.append(p.to_dict())

    return {
        "count": len(products),
        "products": products
    }


def search_policy_faq_tool(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Tool: Retrieve company warranty, replacement, financing, and delivery policies."""
    return search_policies_and_faqs(query=query, top_k=top_k)


def capture_lead_tool(
    db: Session,
    session_id: str,
    customer_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    budget_max: Optional[int] = None,
    preferred_ram: Optional[int] = None,
    purpose: Optional[str] = None,
    product_id: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Tool: Save qualified sales lead in CRM database."""
    lead_data = {
        "session_id": session_id,
        "customer_name": customer_name,
        "email": email,
        "phone": phone,
        "budget_max": budget_max,
        "preferred_ram": preferred_ram,
        "purpose": purpose,
        "interested_product_id": product_id,
        "lead_status": "qualified",
        "notes": notes or "Captured via AI Sales Assistant conversation."
    }
    created_lead = crud.create_lead(db, lead_data)
    return {
        "status": "success",
        "lead_id": created_lead.id,
        "customer_name": created_lead.customer_name,
        "phone": created_lead.phone,
        "email": created_lead.email
    }


def get_conversation_history_tool(db: Session, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
    """Tool: Load recent chat history for session context."""
    messages = crud.get_recent_chat_history(db, session_id, limit=limit)
    return [{"role": m.role, "content": m.content} for m in messages]
