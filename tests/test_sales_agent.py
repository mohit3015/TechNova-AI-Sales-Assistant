"""
=============================================================================
TechNova AI Sales Assistant - AI Sales Agent & Multi-Turn Intelligence Test
=============================================================================
📌 ROLE & PURPOSE:
   Yeh test suite Phase 3 ke Conversational Sales Intelligence ko test karta hai:
   1. Intent Detection: Recommendation, Comparison, Policy/FAQ aur Lead Capture.
   2. Multi-Turn Memory: Turn 1 (Query) -> Turn 2 (Warranty FAQ) -> Turn 3 (Booking & Lead Creation).
   3. API Chat Endpoint: Full end-to-end integration test.

🎯 USE CASE:
   Terminal se chala kar verify karein: `python tests/test_sales_agent.py`.
=============================================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal
from app.agents.intent_detection import IntentDetector, UserIntent
from app.agents.sales_agent import SalesAgent
from app.database import crud


def test_intent_detection():
    print("\n--- 1. Testing Intent Detection & Slot Extraction ---")
    
    # 1. Recommendation
    s1 = IntentDetector.detect("Mujhe 50,000 ke andar ek coding laptop chahiye 16gb ram wala")
    assert s1.intent == UserIntent.RECOMMENDATION
    assert s1.budget_max == 50000
    assert s1.min_ram == 16
    assert "Programming" in (s1.purpose or "")
    print(" S1 (Recommendation):", s1.intent, f"Budget: ₹{s1.budget_max}", f"RAM: {s1.min_ram}GB", f"Purpose: {s1.purpose}")

    # 2. Comparison
    s2 = IntentDetector.detect("P103 aur P104 ko compare karke difference batao")
    assert s2.intent == UserIntent.COMPARISON
    assert "P103" in s2.product_ids and "P104" in s2.product_ids
    print(" S2 (Comparison):", s2.intent, s2.product_ids)

    # 3. Policy / FAQ
    s3 = IntentDetector.detect("Warranty kitne saal ki milti hai aur delivery charges kya hain?")
    assert s3.intent == UserIntent.POLICY_FAQ
    print(" S3 (Policy/FAQ):", s3.intent)

    # 4. Lead Capture
    s4 = IntentDetector.detect("Mera naam Amit Kumar hai aur phone number 9811223344 hai, mujhe laptop book karna hai")
    assert s4.intent == UserIntent.LEAD_CAPTURE
    assert s4.phone == "9811223344"
    assert s4.customer_name == "Amit Kumar"
    print(" S4 (Lead Capture):", s4.intent, f"Name: {s4.customer_name}", f"Phone: {s4.phone}")

    print(" All Intent Detection Tests: PASSED")


def test_multi_turn_sales_conversation():
    print("\n--- 2. Testing End-to-End Multi-Turn Sales Flow ---")
    db = SessionLocal()
    session_id = "test_sales_multi_turn_888"

    # Turn 1: Product recommendation request
    t1_msg = "Mujhe 50,000 ke andar ek laptop chahiye jo coding aur python ke liye best ho."
    print(f"\n[Customer Turn 1]: {t1_msg}")
    res1 = SalesAgent.process_message(db, session_id=session_id, message=t1_msg)
    print(f"[AI Sales Agent]:\n{res1['answer'][:250]}...\n")
    assert len(res1["recommended_products"]) > 0
    top_laptop = res1["recommended_products"][0]
    print(f"-> Recommended: {top_laptop['name']} (₹{top_laptop['price']:,}, {top_laptop['ram_gb']}GB RAM)")
    assert top_laptop["price"] <= 50000

    # Turn 2: FAQ inquiry on warranty & returns
    t2_msg = "Is laptop me warranty kitne saal ki hai aur replacement policy kya hai?"
    print(f"\n[Customer Turn 2]: {t2_msg}")
    res2 = SalesAgent.process_message(db, session_id=session_id, message=t2_msg)
    print(f"[AI Sales Agent]:\n{res2['answer'][:250]}...\n")
    assert any(term in res2["answer"].lower() for term in ["warranty", "replacement", "return", "policy", "technova"])

    # Turn 3: Lead Qualification & Booking intent
    t3_msg = "Great! Mera naam Rahul Sharma hai aur phone 9876543210 hai, mujhe ProBook A book karna hai."
    print(f"\n[Customer Turn 3]: {t3_msg}")
    res3 = SalesAgent.process_message(db, session_id=session_id, message=t3_msg)
    print(f"[AI Sales Agent]:\n{res3['answer']}\n")
    assert res3["lead_captured"] is not None
    assert res3["lead_captured"]["phone"] == "9876543210"
    print(f"-> CRM Lead Created: ID {res3['lead_captured']['lead_id']} for {res3['lead_captured']['customer_name']}")

    # Verify lead in database
    db_leads = crud.get_leads(db, limit=5)
    matched = [l for l in db_leads if l.phone == "9876543210"]
    assert len(matched) > 0
    print(" Multi-Turn Sales Conversation & Lead Capture: PASSED")
    db.close()


def test_api_chat_endpoint():
    print("\n--- 3. Testing POST /api/chat with Sales Agent ---")
    client = TestClient(app)
    payload = {
        "session_id": "api_test_session_999",
        "message": "Namaste, mujhe 60000 ke andar gaming aur editing laptop dikhao"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("API Response Intent:", data["intent"])
    print(f"API Recommended {len(data['recommended_products'])} products:")
    for p in data["recommended_products"]:
        print(f"  • {p['name']} (₹{p['price']:,}, {p['ram_gb']}GB RAM, GPU: {p['gpu']})")
    print(" POST /api/chat: PASSED")


if __name__ == "__main__":
    test_intent_detection()
    test_multi_turn_sales_conversation()
    test_api_chat_endpoint()
    print("\n All Phase 3 AI Sales Intelligence Tests PASSED! ")
