"""
=============================================================================
TechNova AI Sales Assistant - SQLAlchemy Database Models (Schema)
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file hamare SQLite Database (`technova_store.db`) ka Table Schema define karti hai:
   1. `Product`: Authoritative table for laptop specs (price, RAM, processor, GPU, stock count).
   2. `Lead`: Inbound sales inquiries and customer contact information.
   3. `ChatHistory`: Multi-turn conversational session history (user questions & AI answers).

🎯 USE CASE:
   SQLAlchemy ORM in models ko use karke queries execute karta hai aur tables create karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Database tables mein naye columns (e.g., color, discount_percentage) add karne hon.
=============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Product(Base):
    """Authoritative SQL table for product inventory, pricing, and exact hardware specs."""
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="Laptop", index=True)
    brand = Column(String(100), default="TechNova", index=True)
    price = Column(Integer, nullable=False, index=True)  # in INR (₹)
    ram_gb = Column(Integer, nullable=False, index=True)
    storage = Column(String(100), nullable=False)
    processor = Column(String(150), nullable=False)
    gpu = Column(String(150), nullable=False)
    display = Column(String(150), nullable=False)
    battery_life_hours = Column(Float, default=0.0)
    weight_kg = Column(Float, default=0.0)
    stock_count = Column(Integer, default=0, index=True)
    warranty_years = Column(Integer, default=1)
    return_days = Column(Integer, default=7)
    suitable_for = Column(Text, default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "brand": self.brand,
            "price": self.price,
            "ram_gb": self.ram_gb,
            "storage": self.storage,
            "processor": self.processor,
            "gpu": self.gpu,
            "display": self.display,
            "battery_life_hours": self.battery_life_hours,
            "weight_kg": self.weight_kg,
            "stock_count": self.stock_count,
            "warranty_years": self.warranty_years,
            "return_days": self.return_days,
            "suitable_for": self.suitable_for,
            "description": self.description
        }


class Lead(Base):
    """Customer CRM records captured by AI Sales Assistant during conversations."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=True)
    customer_name = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    budget_max = Column(Integer, nullable=True)
    preferred_ram = Column(Integer, nullable=True)
    purpose = Column(String(250), nullable=True)
    interested_product_id = Column(String(50), nullable=True)
    lead_status = Column(String(50), default="qualified")  # new, qualified, contacted, converted
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "customer_name": self.customer_name,
            "email": self.email,
            "phone": self.phone,
            "budget_max": self.budget_max,
            "preferred_ram": self.preferred_ram,
            "purpose": self.purpose,
            "interested_product_id": self.interested_product_id,
            "lead_status": self.lead_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ChatHistory(Base):
    """Persisted conversation history for multi-turn sessions."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
