"""
=============================================================================
TechNova AI Sales Assistant - Automated FastAPI Endpoints Test Suite
=============================================================================
📌 ROLE & PURPOSE:
   Yeh test suite FastAPI backend ke sabhi primary REST endpoints ko test karta hai:
   - `GET /health`: SQLite aur ChromaDB live status verify karta hai.
   - `GET /api/products`: Catalog listing aur budget/RAM filters test karta hai.
   - `POST /api/products/compare`: 2 laptops ka side-by-side spec comparison test karta hai.
   - `POST & GET /api/leads`: Customer lead registration aur CRM list fetch test karta hai.
   - `POST /api/chat`: Hybrid Retrieval pipeline test karta hai.

🎯 USE CASE:
   Terminal se chala kar verify karein: `pytest tests/test_api.py` ya `python tests/test_api.py`.
=============================================================================
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    print("\n--- 1. Testing GET /health ---")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    data = response.json()
    print("Health response:", data)
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "healthy"
    assert data["vector_database"]["indexed_chunks"] > 0
    print(" GET /health: PASSED")


def test_products_list_and_filter():
    print("\n--- 2. Testing GET /api/products ---")
    # All products
    res_all = client.get("/api/products")
    assert res_all.status_code == 200
    products = res_all.json()
    print(f"Total products returned: {len(products)}")
    assert len(products) > 0

    # Filtered products (Budget <= 50000 and RAM >= 16GB)
    res_filtered = client.get("/api/products?max_price=50000&min_ram=16")
    assert res_filtered.status_code == 200
    filtered = res_filtered.json()
    print(f"Filtered products (<= 50k & >= 16GB): {len(filtered)}")
    for p in filtered:
        print(f"  -> {p['name']} (₹{p['price']:,}, {p['ram_gb']}GB RAM)")
        assert p["price"] <= 50000
        assert p["ram_gb"] >= 16
    print(" GET /api/products: PASSED")


def test_products_compare():
    print("\n--- 3. Testing POST /api/products/compare ---")
    payload = {"product_ids": ["P103", "P104"]}
    response = client.post("/api/products/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"Compared {data['compared_count']} products:")
    for p in data["products"]:
        print(f"  -> {p['name']} (Processor: {p['processor']}, GPU: {p['gpu']})")
    assert data["compared_count"] == 2
    print(" POST /api/products/compare: PASSED")


def test_create_and_fetch_lead():
    print("\n--- 4. Testing POST & GET /api/leads ---")
    lead_payload = {
        "session_id": "test_session_101",
        "customer_name": "Rohan Sharma",
        "email": "rohan.sharma@example.com",
        "phone": "+91-9876543210",
        "budget_max": 50000,
        "preferred_ram": 16,
        "purpose": "Python & Data Analysis",
        "interested_product_id": "P103",
        "notes": "Looking for urgent delivery"
    }
    post_res = client.post("/api/leads", json=lead_payload)
    assert post_res.status_code == 201
    created = post_res.json()
    print("Created Lead:", created["id"], created["customer_name"])
    assert created["email"] == lead_payload["email"]

    # Verify listing
    get_res = client.get("/api/leads")
    assert get_res.status_code == 200
    leads = get_res.json()
    print(f"Total leads in system: {len(leads)}")
    assert any(l["email"] == "rohan.sharma@example.com" for l in leads)
    print(" POST & GET /api/leads: PASSED")


def test_hybrid_chat_endpoint():
    print("\n--- 5. Testing POST /api/chat (Hybrid Search) ---")
    chat_payload = {
        "session_id": "sess_demo_101",
        "message": "Coding aur web development ke liye laptop chahiye under 50000",
        "max_price": 50000,
        "min_ram": 16
    }
    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 200
    data = response.json()
    print(f"Products recommended by Hybrid Retriever: {data['products_found_count']}")
    for prod in data["recommended_products"]:
        print(f"  [Score: {prod.get('rerank_score', 0):.2f}] {prod['name']} (₹{prod['price']:,}, {prod['ram_gb']}GB RAM)")
    print(f"Policy/FAQ chunks retrieved: {len(data['policy_and_faq_context'])}")
    print(f"Sources: {data['sources']}")
    assert data["products_found_count"] > 0
    print(" POST /api/chat: PASSED")


if __name__ == "__main__":
    test_health_endpoint()
    test_products_list_and_filter()
    test_products_compare()
    test_create_and_fetch_lead()
    test_hybrid_chat_endpoint()
    print("\n All Phase 2 Tests PASSED Successfully! ")
