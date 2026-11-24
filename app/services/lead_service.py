"""
=============================================================================
TechNova AI Sales Assistant - Lead Management Service Layer
=============================================================================
📌 ROLE & PURPOSE:
   Yeh Service Layer sales leads aur customer reservation handling ka logic encapsulate karti hai:
   - Lead creation validation.
   - Lead retrieval aur status updates (qualified, contacted, converted).

🎯 USE CASE:
   `app/api/leads.py` is service ko call karke lead records manage karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - CRM integration (e.g., Salesforce, HubSpot, Zoho CRM webhook) add karna ho.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import crud
from app.database.models import Lead


class LeadService:
    @staticmethod
    def create_sales_lead(db: Session, lead_data: Dict[str, Any]) -> Lead:
        """Validate and create a customer sales lead."""
        return crud.create_lead(db, lead_data)

    @staticmethod
    def get_all_leads(db: Session, limit: int = 50) -> List[Lead]:
        """Fetch captured leads for CRM display and export."""
        return crud.get_leads(db, limit=limit)
