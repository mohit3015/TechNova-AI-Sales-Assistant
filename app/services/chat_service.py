"""
=============================================================================
TechNova AI Sales Assistant - Chat Service Layer
=============================================================================
📌 ROLE & PURPOSE:
   Yeh Service Layer API endpoints (`/api/chat`) aur core business logic (`SalesAgent`)
   ke beech coordinator ka kaam karti hai. Isse Clean Architecture maintain rehti hai.

🎯 USE CASE:
   `app/api/chat.py` is service ko call karta hai to process incoming user messages.

🛠️ WHEN TO MODIFY THIS FILE:
   - Agar chat request process hone se pehle koi analytics ya extra validation add karni ho.
=============================================================================
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.sales_agent import SalesAgent


class ChatService:
    @staticmethod
    def process_chat_turn(
        db: Session,
        session_id: str,
        message: str,
        max_price: Optional[int] = None,
        min_ram: Optional[int] = None,
        brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """Service coordinator for processing user messages through the Sales Agent."""
        return SalesAgent.process_message(
            db=db,
            session_id=session_id,
            message=message,
            max_price_override=max_price,
            min_ram_override=min_ram,
            brand_override=brand
        )
