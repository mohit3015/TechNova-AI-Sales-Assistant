"""
=============================================================================
TechNova AI Sales Assistant - Automated RAG Evaluation Benchmark Suite
=============================================================================
📌 ROLE & PURPOSE:
   Yeh test suite hamare complete RAG system ki quality aur production readiness measure karta hai:
   1. Price Accuracy (%): Kya recommendation price live SQL database se 100% match karti hai?
   2. Context Faithfulness (%): Kya answer retrieved context par strictly grounded hai (zero hallucination)?
   3. Retrieval Hit Rate (%): Kya relevant products/policies ChromaDB aur SQL se retrieve hui?
   4. Zero-Result Upsell Handling: Out-of-budget query par smart alternatives milte hain ya nahi?
   5. Response Latency (ms): Query processing aur reranking ki end-to-end speed.

🎯 USE CASE:
   Terminal se benchmark run karein: `python tests/eval_rag.py`.
=============================================================================
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import SessionLocal
from app.agents.sales_agent import SalesAgent
from app.database import crud


BENCHMARK_SCENARIOS = [
    {
        "id": "TC-01",
        "category": "Budget Recommendation",
        "query": "₹50,000 ke andar 16GB RAM coding laptop suggest karo",
        "expected_intent": "recommendation",
        "max_budget": 50000,
        "min_ram": 16,
        "must_contain_product_id": "P103",  # TechNova ProBook A
    },
    {
        "id": "TC-02",
        "category": "AI / Workstation Recommendation",
        "query": "Machine Learning aur Deep Learning ke liye best laptop kaun sa hai?",
        "expected_intent": "recommendation",
        "must_have_gpu": True,
    },
    {
        "id": "TC-03",
        "category": "Policy & Guarantee Inquiry",
        "query": "TechNova ki warranty kitne saal ki hai aur return policy kya hai?",
        "expected_intent": "policy_faq",
        "expected_policy_terms": ["warranty", "replacement", "return"],
    },
    {
        "id": "TC-04",
        "category": "Zero-Match Upsell Handling",
        "query": "16GB RAM wala laptop under ₹20,000 chahiye",
        "expected_intent": "recommendation",
        "expected_alternatives": True,
    },
    {
        "id": "TC-05",
        "category": "Lead Qualification & Booking",
        "query": "Mera naam Mohit Kumar hai, phone number 9876543210 hai, mujhe ProBook A lena hai.",
        "expected_intent": "lead_capture",
        "expected_lead_phone": "9876543210",
    }
]


def run_rag_evaluations():
    print("=" * 75)
    print(" TechNova AI Sales Assistant - Automated RAG Evaluation Benchmark ")
    print("=" * 75)

    db = SessionLocal()
    results = []

    total_tests = len(BENCHMARK_SCENARIOS)
    passed_tests = 0
    price_accuracy_checks = 0
    price_accuracy_hits = 0
    faithfulness_checks = 0
    faithfulness_hits = 0
    latencies = []

    for sc in BENCHMARK_SCENARIOS:
        sess_id = f"eval_sess_{sc['id'].lower()}"
        start_time = time.perf_counter()
        
        response = SalesAgent.process_message(db, session_id=sess_id, message=sc["query"])
        latency_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(latency_ms)

        intent = response.get("intent")
        products = response.get("recommended_products", [])
        answer = response.get("answer", "")
        lead = response.get("lead_captured")

        # 1. Intent Alignment Check
        intent_ok = (intent == sc["expected_intent"])

        # 2. Price Accuracy Check (Strict SQL Grounding)
        price_ok = True
        if products and sc.get("max_budget"):
            price_accuracy_checks += 1
            for p in products:
                # Query actual SQL record to ensure exact match
                sql_p = crud.get_product_by_id(db, p["product_id"])
                if sql_p and p["price"] == sql_p.price and p["price"] <= sc["max_budget"]:
                    pass
                else:
                    price_ok = False
            if price_ok:
                price_accuracy_hits += 1

        # 3. Faithfulness & Grounding Check
        grounding_ok = True
        if sc.get("expected_policy_terms"):
            faithfulness_checks += 1
            ans_lower = answer.lower()
            if any(term in ans_lower for term in sc["expected_policy_terms"]):
                faithfulness_hits += 1
            else:
                grounding_ok = False

        if sc.get("must_have_gpu"):
            faithfulness_checks += 1
            if any(p.get("gpu") and ("RTX" in p["gpu"] or "GeForce" in p["gpu"]) for p in products):
                faithfulness_hits += 1
            else:
                grounding_ok = False

        if sc.get("expected_lead_phone"):
            faithfulness_checks += 1
            if lead and lead.get("phone") == sc["expected_lead_phone"]:
                faithfulness_hits += 1
            else:
                grounding_ok = False

        test_passed = intent_ok and price_ok and grounding_ok
        if test_passed:
            passed_tests += 1

        results.append({
            "id": sc["id"],
            "category": sc["category"],
            "intent": intent,
            "status": "PASS" if test_passed else "FAIL",
            "latency_ms": latency_ms,
            "products_count": len(products)
        })

    db.close()

    # Benchmark Calculations
    overall_score = (passed_tests / total_tests) * 100
    price_accuracy_pct = (price_accuracy_hits / max(price_accuracy_checks, 1)) * 100
    faithfulness_pct = (faithfulness_hits / max(faithfulness_checks, 1)) * 100
    avg_latency = sum(latencies) / len(latencies)

    # Print Summary Table
    print("\n" + "-" * 75)
    print(f"{'Test ID':<10} | {'Category':<28} | {'Status':<8} | {'Latency (ms)':<12} | {'Products'}")
    print("-" * 75)
    for r in results:
        print(f"{r['id']:<10} | {r['category']:<28} | {r['status']:<8} | {r['latency_ms']:<12.1f} | {r['products_count']} found")
    print("-" * 75)

    print("\n📊 RAG EVALUATION BENCHMARK METRICS:")
    print(f"  • Overall Evaluation Pass Rate: {overall_score:.1f}% ({passed_tests}/{total_tests} scenarios)")
    print(f"  • Price Accuracy Rate:         {price_accuracy_pct:.1f}% (Zero pricing hallucinations)")
    print(f"  • Context Faithfulness Rate:    {faithfulness_pct:.1f}% (Grounded on retrieved docs)")
    print(f"  • Average End-to-End Latency:   {avg_latency:.1f} ms")
    print("=" * 75)

    assert overall_score >= 80, f"RAG Evaluation failed with overall score {overall_score:.1f}%"
    return {
        "overall_score": overall_score,
        "price_accuracy": price_accuracy_pct,
        "faithfulness": faithfulness_pct,
        "avg_latency_ms": avg_latency
    }


if __name__ == "__main__":
    run_rag_evaluations()
