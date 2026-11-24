"""
=============================================================================
TechNova AI Sales Assistant - Products Catalog API Endpoints
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file laptops catalog aur live inventory ke REST API endpoints provide karti hai:
   1. `GET /api/products`: Filtered products search (by budget, min RAM, brand, in-stock).
   2. `GET /api/products/{id}`: Single product ki live details aur stock status.
   3. `POST /api/products/compare`: 2 se 4 laptops ka side-by-side specification comparison.

🎯 USE CASE:
   Frontend ka Catalog tab aur comparison tool live data ke liye inhi endpoints ko call karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Naye catalog filtering parameters add karne hon.
=============================================================================
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database import crud


router = APIRouter(prefix="/products", tags=["Products"])


class ProductResponse(BaseModel):
    product_id: str
    name: str
    category: str
    brand: str
    price: int
    ram_gb: int
    storage: str
    processor: str
    gpu: str
    display: str
    battery_life_hours: float
    weight_kg: float
    stock_count: int
    warranty_years: int
    return_days: int
    suitable_for: str
    description: str

    class Config:
        from_attributes = True


class CompareRequest(BaseModel):
    product_ids: List[str]


@router.get("", response_model=List[ProductResponse])
def get_products(
    max_price: Optional[int] = Query(None, description="Maximum budget in INR"),
    min_ram: Optional[int] = Query(None, description="Minimum RAM in GB"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    in_stock_only: bool = Query(True, description="Only show in-stock products"),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Retrieve catalog products with optional budget and hardware filters."""
    products = crud.list_products(
        db=db,
        max_price=max_price,
        min_ram=min_ram,
        brand=brand,
        in_stock_only=in_stock_only,
        limit=limit
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Fetch exact product details and live inventory status."""
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
    return product


@router.post("/compare")
def compare_products(request: CompareRequest, db: Session = Depends(get_db)):
    """Compare specifications of 2 or more products side-by-side."""
    if len(request.product_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 product IDs are required for comparison.")
    if len(request.product_ids) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 products can be compared simultaneously.")

    products = []
    for pid in request.product_ids:
        prod = crud.get_product_by_id(db, pid.strip())
        if prod:
            products.append(prod.to_dict())

    if not products:
        raise HTTPException(status_code=404, detail="None of the specified products were found.")

    return {
        "compared_count": len(products),
        "products": products
    }
