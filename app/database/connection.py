"""
=============================================================================
TechNova AI Sales Assistant - Database Connection & Session Management
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file SQLite database engine connect karti hai aur session lifecycle manage karti hai:
   1. `init_db()`: Tables automatically create karti hai agar woh pehle se exist na karein.
   2. `SessionLocal`: Database sessions create karne ka factory instance.
   3. `get_db()`: FastAPI dependency jo har API request ko safe, isolated DB session deti hai aur baad mein close karti hai.

🎯 USE CASE:
   Har database interaction (CRUD operations, Seeding, Tests) is connection file se start hota hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - SQLite se PostgreSQL ya MySQL par switch karna ho toh connection string yahan change hogi.
=============================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.models import Base

# SQLite configuration
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI Dependency for database session management."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
