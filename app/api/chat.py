"""
=============================================================================
TechNova AI Sales Assistant - Chat API Endpoint
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file customer chat requests ke liye primary REST API endpoint (`POST /api/chat`) provide karti hai.
   Isme:
   1. `ChatRequest` Pydantic model: Request validation (session_id, message, budget filters).
   2. `ChatResponse` Pydantic model: Structured output (answer, recommended_products, sources).
   3. `ChatService.process_chat_turn()` ko call karke full AI sales pipeline chalata hai.

🎯 USE CASE:
   Streamlit frontend ka chat box jab bhi message bhejta hai, yeh endpoint request handle karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Chat API ke request/response format mein naye fields add karne hon.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["Chat & Sales Assistance"])


class ChatRequest(BaseModel):
    session_id: str
    message: str
    max_price: Optional[int] = None
    min_ram: Optional[int] = None
    brand: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    message: str
    intent: str
    answer: str
    recommended_products: List[Dict[str, Any]]
    policy_and_faq_context: List[Dict[str, Any]]
    lead_captured: Optional[Dict[str, Any]] = None
    sources: List[str]


@router.post("", response_model=ChatResponse)
def handle_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Primary conversational endpoint for customer interaction with AI Sales Assistant."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = ChatService.process_chat_turn(
        db=db,
        session_id=request.session_id,
        message=request.message,
        max_price=request.max_price,
        min_ram=request.min_ram,
        brand=request.brand
    )

    return result
