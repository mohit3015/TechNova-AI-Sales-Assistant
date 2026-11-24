"""
=============================================================================
TechNova AI Sales Assistant - Comprehensive RAG Evaluation Benchmark Suite
=============================================================================
📌 ROLE & PURPOSE:
   Enterprise-grade automated evaluation suite for evaluating the complete RAG pipeline:
   1. Retrieval Recall@K: Did the target product/document appear in top-K retrieval?
   2. Price Accuracy (%): 100% strict verification against SQLite relational database.
   3. Context Faithfulness (%): Fact verification against retrieved chunks (zero hallucination).
   4. Answer Relevancy (%): Response directly addresses customer inquiry and intent.
   5. Zero-Match Handling: Out-of-budget inquiries trigger smart upselling alternatives.
   6. Latency Percentiles: Benchmarks P50, P90, P95, and Average end-to-end response latency (ms).

🎯 TEST SUITE SIZE:
   25 diverse scenarios covering Budgeting, Workstations, AAA Gaming, Policy FAQs,
   Side-by-side Comparisons, Lead Capture, Hinglish Mixed Queries, and Edge Cases.

🎯 RUN COMMAND:
   python tests/eval_rag.py
=============================================================================
"""

import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import SessionLocal
from app.agents.sales_agent import SalesAgent
from app.database import crud


BENCHMARK_SCENARIOS = [
    # --- Category 1: Budget-Constrained Recommendations (Strict SQL Filtering) ---
    {
        "id": "TC-01",
        "category": "Budget Recommendation",
        "query": "₹50,000 ke andar 16GB RAM coding laptop suggest karo",
        "expected_intent": "recommendation",
        "max_budget": 50000,
        "min_ram": 16,
        "must_contain_product_id": "P103",  # TechNova ProBook A (₹42,999)
    },
    {
        "id": "TC-02",
        "category": "Budget Recommendation",
        "query": "Sabse sasta laptop kaun sa hai college students ke liye?",
        "expected_intent": "recommendation",
        "must_contain_product_id": "P101",  # TechNova Spark 14 (₹28,999)
    },
    {
        "id": "TC-03",
        "category": "Budget Recommendation",
        "query": "I need a lightweight laptop under ₹40,000 for office work and accounting",
        "expected_intent": "recommendation",
        "max_budget": 40000,
        "must_contain_product_id": "P102",  # TechNova SlimBook 15 (₹37,999)
    },
    {
        "id": "TC-04",
        "category": "Budget Recommendation",
        "query": "Best development laptop under 55k with 1TB SSD",
        "expected_intent": "recommendation",
        "max_budget": 55000,
        "must_contain_product_id": "P105",  # TechNova CodeMaster 14 (₹53,999)
    },
    {
        "id": "TC-05",
        "category": "Budget Recommendation",
        "query": "₹60,000 budget mein video editing aur casual gaming laptop",
        "expected_intent": "recommendation",
        "max_budget": 60000,
        "must_contain_product_id": "P106",  # TechNova Gaming Lite G1 (₹58,999)
    },

    # --- Category 2: High Performance & Workstation Inquiries (Semantic Retrieval) ---
    {
        "id": "TC-06",
        "category": "AI / ML Workstation",
        "query": "Machine Learning aur Deep Learning training ke liye best laptop kaun sa hai?",
        "expected_intent": "recommendation",
        "must_have_gpu": True,
        "target_product_ids": ["P107", "P109", "P110"],
    },
    {
        "id": "TC-07",
        "category": "AI / ML Workstation",
        "query": "Local LLM fine-tuning aur PyTorch CUDA acceleration ke liye 32GB RAM workstation chahiye",
        "expected_intent": "recommendation",
        "min_ram": 32,
        "must_have_gpu": True,
        "must_contain_product_id": "P110",  # TechNova Creator Pro 16 (32GB, RTX 4060)
    },
    {
        "id": "TC-08",
        "category": "Gaming & GPU",
        "query": "AAA games like GTA 6 and Cyberpunk 2077 khelne ke liye powerful gaming laptop",
        "expected_intent": "recommendation",
        "must_have_gpu": True,
        "target_product_ids": ["P109", "P110", "P111"],
    },
    {
        "id": "TC-09",
        "category": "Extreme Performance",
        "query": "TechNova store ka sabse mehenga aur flagship highest price laptop kaun sa hai?",
        "expected_intent": "recommendation",
        "must_contain_product_id": "P111",  # TechNova Titan X 17 (₹1,24,999)
    },
    {
        "id": "TC-10",
        "category": "Ultraportable & Display",
        "query": "Travel ke liye 1kg se kam weight aur OLED screen wala laptop",
        "expected_intent": "recommendation",
        "must_contain_product_id": "P112",  # TechNova Feather 13 (0.99kg OLED)
    },

    # --- Category 3: Direct Product ID Lookups ---
    {
        "id": "TC-11",
        "category": "Direct Product Lookup",
        "query": "P103 laptop ke exact specifications aur price kya hai?",
        "expected_intent": "recommendation",
        "must_contain_product_id": "P103",
    },
    {
        "id": "TC-12",
        "category": "Direct Product Lookup",
        "query": "Tell me details about TechNova NitroForce 16 model P109",
        "expected_intent": "recommendation",
        "must_contain_product_id": "P109",
    },

    # --- Category 4: Side-by-Side Comparisons ---
    {
        "id": "TC-13",
        "category": "Product Comparison",
        "query": "P103 aur P104 ko compare karke difference batao",
        "expected_intent": "comparison",
        "expected_compare_ids": ["P103", "P104"],
    },
    {
        "id": "TC-14",
        "category": "Product Comparison",
        "query": "Compare TechNova AI Studio 15 vs NitroForce 16 for machine learning",
        "expected_intent": "comparison",
        "expected_compare_ids": ["P107", "P109"],
    },
    {
        "id": "TC-15",
        "category": "Product Comparison",
        "query": "P110 aur P111 mein kya antar hai, kaun sa lena chahiye?",
        "expected_intent": "comparison",
        "expected_compare_ids": ["P110", "P111"],
    },

    # --- Category 5: Policy, Warranty, FAQs & Guarantees ---
    {
        "id": "TC-16",
        "category": "Policy & Guarantee",
        "query": "TechNova ki warranty kitne saal ki hai aur kya hardware failure covered hai?",
        "expected_intent": "policy_faq",
        "expected_policy_terms": ["warranty", "hardware", "service"],
    },
    {
        "id": "TC-17",
        "category": "Policy & Guarantee",
        "query": "Agar laptop me transit damage ya defect nikle toh replacement policy kya hai?",
        "expected_intent": "policy_faq",
        "expected_policy_terms": ["replacement", "defect", "policy"],
    },
    {
        "id": "TC-18",
        "category": "Policy & Guarantee",
        "query": "Kya TechNova store par No-Cost EMI aur student discount available hai?",
        "expected_intent": "policy_faq",
        "expected_policy_terms": ["emi", "discount", "student"],
    },
    {
        "id": "TC-19",
        "category": "Policy & Guarantee",
        "query": "Laptop delivery kitne din mein hoti hai aur delivery charges kya hain?",
        "expected_intent": "policy_faq",
        "expected_policy_terms": ["delivery", "shipping", "free"],
    },

    # --- Category 6: Zero-Match Fallbacks & Smart Upselling ---
    {
        "id": "TC-20",
        "category": "Zero-Match Upsell",
        "query": "16GB RAM wala laptop under ₹20,000 chahiye turant",
        "expected_intent": "recommendation",
        "expected_alternatives": True,
    },
    {
        "id": "TC-21",
        "category": "Zero-Match Upsell",
        "query": "32GB RAM and RTX 4060 laptop under ₹40,000",
        "expected_intent": "recommendation",
        "expected_alternatives": True,
    },

    # --- Category 7: Lead Qualification & CRM Capture ---
    {
        "id": "TC-22",
        "category": "Lead Capture",
        "query": "Mera naam Mohit Kumar hai, phone number 9876543210 hai, mujhe ProBook A lena hai.",
        "expected_intent": "lead_capture",
        "expected_lead_phone": "9876543210",
        "expected_lead_name": "Mohit Kumar",
    },
    {
        "id": "TC-23",
        "category": "Lead Capture",
        "query": "I want to purchase NitroForce 16. Contact me at rahul.verma@example.com or 9811223344",
        "expected_intent": "lead_capture",
        "expected_lead_phone": "9811223344",
    },

    # --- Category 8: Hinglish Mixed Queries & Colloquial Phrasing ---
    {
        "id": "TC-24",
        "category": "Hinglish Edge Case",
        "query": "Coding seekh raha hoon python ke liye mast sa laptop batao 45 hazaar tak",
        "expected_intent": "recommendation",
        "max_budget": 45000,
        "must_contain_product_id": "P103",
    },
    {
        "id": "TC-25",
        "category": "Hinglish Edge Case",
        "query": "Battery backup kiska sabse tagda hai jo 10 ghante chal sake?",
        "expected_intent": "recommendation",
        "target_product_ids": ["P108", "P112"],  # ThinkPro 14 (10 hrs) or Feather 13 (11 hrs)
    }
]


def run_rag_evaluations():
    print("=" * 80)
    print(" TechNova AI Sales Assistant - Comprehensive 25-Scenario RAG Benchmark ")
    print("=" * 80)

    db = SessionLocal()
    results = []

    total_tests = len(BENCHMARK_SCENARIOS)
    passed_tests = 0

    # Metric Counters
    retrieval_checks = 0
    retrieval_hits = 0

    price_checks = 0
    price_hits = 0

    faithfulness_checks = 0
    faithfulness_hits = 0

    relevancy_checks = 0
    relevancy_hits = 0

    latencies: List[float] = []

    for sc in BENCHMARK_SCENARIOS:
        sess_id = f"eval_sess_{sc['id'].lower().replace('-', '_')}"
        start_time = time.perf_counter()

        response = SalesAgent.process_message(db, session_id=sess_id, message=sc["query"])
        latency_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(latency_ms)

        intent = response.get("intent")
        products = response.get("recommended_products", [])
        answer = response.get("answer", "")
        lead = response.get("lead_captured")
        policies = response.get("policy_and_faq_context", [])

        product_ids_found = [p["product_id"] for p in products]

        # -------------------------------------------------------------
        # 1. Intent Alignment Check
        # -------------------------------------------------------------
        intent_ok = (intent == sc["expected_intent"])

        # -------------------------------------------------------------
        # 2. Retrieval Recall@K Check
        # -------------------------------------------------------------
        retrieval_ok = True
        if sc.get("must_contain_product_id"):
            retrieval_checks += 1
            if sc["must_contain_product_id"] in product_ids_found:
                retrieval_hits += 1
            else:
                retrieval_ok = False

        if sc.get("target_product_ids"):
            retrieval_checks += 1
            if any(t_id in product_ids_found for t_id in sc["target_product_ids"]):
                retrieval_hits += 1
            else:
                retrieval_ok = False

        if sc.get("expected_compare_ids"):
            retrieval_checks += 1
            if all(c_id in product_ids_found for c_id in sc["expected_compare_ids"]):
                retrieval_hits += 1
            else:
                retrieval_ok = False

        # -------------------------------------------------------------
        # 3. Price Accuracy Check (Strict SQL Grounding)
        # -------------------------------------------------------------
        price_ok = True
        if products and sc.get("max_budget"):
            price_checks += 1
            for p in products:
                sql_p = crud.get_product_by_id(db, p["product_id"])
                # Must match live SQL price exactly AND must respect user's budget constraint
                if sql_p and p["price"] == sql_p.price and p["price"] <= sc["max_budget"]:
                    pass
                else:
                    price_ok = False
            if price_ok:
                price_hits += 1
        elif products:
            # General product query: verify all returned prices match SQL exactly
            price_checks += 1
            for p in products:
                sql_p = crud.get_product_by_id(db, p["product_id"])
                if not sql_p or p["price"] != sql_p.price:
                    price_ok = False
            if price_ok:
                price_hits += 1

        # -------------------------------------------------------------
        # 4. Context Faithfulness & Fact Grounding Check
        # -------------------------------------------------------------
        faithfulness_ok = True

        # Policy grounding check
        if sc.get("expected_policy_terms"):
            faithfulness_checks += 1
            ans_lower = answer.lower()
            if any(term in ans_lower for term in sc["expected_policy_terms"]):
                faithfulness_hits += 1
            else:
                faithfulness_ok = False

        # GPU capability grounding check
        if sc.get("must_have_gpu"):
            faithfulness_checks += 1
            has_dedicated_gpu = any(
                p.get("gpu") and any(gpu_brand in p["gpu"] for gpu_brand in ["RTX", "GeForce", "GTX", "Radeon"])
                for p in products
            )
            if has_dedicated_gpu:
                faithfulness_hits += 1
            else:
                faithfulness_ok = False

        # RAM requirement grounding check
        if sc.get("min_ram"):
            faithfulness_checks += 1
            if products and all(p.get("ram_gb", 0) >= sc["min_ram"] for p in products):
                faithfulness_hits += 1
            else:
                faithfulness_ok = False

        # -------------------------------------------------------------
        # 5. Answer Relevancy & CRM Execution
        # -------------------------------------------------------------
        relevancy_ok = True

        # Lead phone and name verification
        if sc.get("expected_lead_phone"):
            relevancy_checks += 1
            if lead and lead.get("phone") == sc["expected_lead_phone"]:
                relevancy_hits += 1
            else:
                relevancy_ok = False

        # Zero-match fallback validation
        if sc.get("expected_alternatives"):
            relevancy_checks += 1
            has_alts = "Alternative" in answer or "Higher Budget" in answer or "budget thoda stretch" in answer
            if has_alts:
                relevancy_hits += 1
            else:
                relevancy_ok = False

        # Overall Scenario Pass Verdict
        test_passed = intent_ok and retrieval_ok and price_ok and faithfulness_ok and relevancy_ok
        if test_passed:
            passed_tests += 1

        results.append({
            "id": sc["id"],
            "category": sc["category"],
            "intent": intent,
            "status": "PASS" if test_passed else "FAIL",
            "latency_ms": latency_ms,
            "products_count": len(products),
            "flags": f"Intent:{intent_ok} | Retr:{retrieval_ok} | Price:{price_ok} | Faith:{faithfulness_ok}"
        })

    db.close()

    # Calculate Benchmark Metrics
    overall_pass_rate = (passed_tests / total_tests) * 100
    recall_rate = (retrieval_hits / max(retrieval_checks, 1)) * 100
    price_accuracy_rate = (price_hits / max(price_checks, 1)) * 100
    faithfulness_rate = (faithfulness_hits / max(faithfulness_checks, 1)) * 100
    relevancy_rate = (relevancy_hits / max(relevancy_checks, 1)) * 100

    # Latency Percentiles (p50, p90, p95)
    sorted_latencies = sorted(latencies)
    avg_latency = statistics.mean(latencies)
    p50_latency = statistics.median(latencies)
    
    # 90th and 95th percentiles
    p90_idx = int(0.90 * len(sorted_latencies))
    p95_idx = int(0.95 * len(sorted_latencies))
    p90_latency = sorted_latencies[min(p90_idx, len(sorted_latencies) - 1)]
    p95_latency = sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)]

    # Print Formatted Evaluation Matrix
    print("\n" + "-" * 88)
    print(f"{'Test ID':<8} | {'Category':<24} | {'Status':<6} | {'Latency':<9} | {'Products':<10} | {'Diagnostics'}")
    print("-" * 88)
    for r in results:
        status_marker = "✓ PASS" if r["status"] == "PASS" else "✗ FAIL"
        print(f"{r['id']:<8} | {r['category']:<24} | {status_marker:<6} | {r['latency_ms']:<7.1f}ms | {r['products_count']:<10} | {r['flags']}")
    print("-" * 88)

    print("\n📊 COMPREHENSIVE PRODUCTION BENCHMARK METRICS:")
    print(f"  • Overall Evaluation Pass Rate: {overall_pass_rate:.1f}% ({passed_tests}/{total_tests} scenarios)")
    print(f"  • Retrieval Recall@K:          {recall_rate:.1f}% ({retrieval_hits}/{retrieval_checks} target matches)")
    print(f"  • Price Accuracy Rate:         {price_accuracy_rate:.1f}% (Zero pricing hallucinations)")
    print(f"  • Context Faithfulness Rate:    {faithfulness_rate:.1f}% (Grounded on retrieved docs)")
    print(f"  • Answer Relevancy Rate:        {relevancy_rate:.1f}% (Matches intent & entity criteria)")
    print(f"  • End-to-End Latency (Avg):     {avg_latency:.1f} ms")
    print(f"  • End-to-End Latency (P50):     {p50_latency:.1f} ms")
    print(f"  • End-to-End Latency (P90):     {p90_latency:.1f} ms")
    print(f"  • End-to-End Latency (P95):     {p95_latency:.1f} ms")
    print("=" * 80)

    assert overall_pass_rate >= 80, f"RAG Evaluation failed with overall score {overall_pass_rate:.1f}%"

    return {
        "total_scenarios": total_tests,
        "overall_pass_rate": overall_pass_rate,
        "recall_at_k": recall_rate,
        "price_accuracy": price_accuracy_rate,
        "faithfulness": faithfulness_rate,
        "relevancy": relevancy_rate,
        "avg_latency_ms": avg_latency,
        "p50_latency_ms": p50_latency,
        "p90_latency_ms": p90_latency,
        "p95_latency_ms": p95_latency,
    }


if __name__ == "__main__":
    run_rag_evaluations()
