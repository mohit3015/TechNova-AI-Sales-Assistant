"""
=============================================================================
TechNova AI Sales Assistant - Autonomous Sales Agent Orchestrator
=============================================================================
📌 ROLE & PURPOSE:
   Yeh hamare chatbot ka Central Brain (AI Agent) hai. Iska workflow:
   1. Multi-Turn Session Memory: SQLite se pichhle conversations padhta hai.
   2. Context Carryover: Agar user Turn 2 par budget na bole, toh Turn 1 ka budget yaad rakhta hai.
   3. Intent-Based Routing:
      - Recommendation -> Hybrid Retrieval search run karta hai.
      - Comparison -> 2 laptops compare karta hai.
      - Policy/FAQ -> Warranty aur return rules nikaalta hai.
      - Lead Capture -> CRM mein lead save karke confirmation deta hai.
   4. LLM Generation: Grounded sales response generate karta hai.
   5. Session Persistence: Both user message aur assistant answer ko SQLite mein save karta hai.

🎯 USE CASE:
   FastAPI `/api/chat` endpoint is agent ko call karta hai har turn ko process karne ke liye.

🛠️ WHEN TO MODIFY THIS FILE:
   - Conversational routing logic, lead capture behavior ya memory depth customize karne ke liye.
=============================================================================
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.database import crud
from app.agents.intent_detection import IntentDetector, UserIntent, ExtractedSlots
from app.agents import tools
from app.llm.prompts import build_sales_rag_prompt
from app.llm.generator import LLMGenerator


class SalesAgent:
    """Core AI Sales Agent orchestrator with multi-turn memory, intent routing, and grounded generation."""

    @classmethod
    def process_message(
        cls,
        db: Session,
        session_id: str,
        message: str,
        max_price_override: Optional[int] = None,
        min_ram_override: Optional[int] = None,
        brand_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process incoming user turn through the sales intelligence pipeline."""
        
        # 1. Retrieve Recent Conversation Memory
        recent_history = tools.get_conversation_history_tool(db, session_id, limit=6)

        # 2. Extract Intent and Slots
        slots = IntentDetector.detect(message)
        
        # Apply API overrides if provided
        budget = max_price_override or slots.budget_max
        min_ram = min_ram_override or slots.min_ram
        brand = brand_override or slots.brand

        # 3. Multi-Turn Context Carryover:
        # If budget or RAM is missing in current message, look back at recent conversation turns
        if budget is None and recent_history:
            for past_msg in reversed(recent_history):
                if past_msg["role"] == "user":
                    past_budget = IntentDetector.extract_budget(past_msg["content"])
                    if past_budget:
                        budget = past_budget
                        break

        if min_ram is None and recent_history:
            for past_msg in reversed(recent_history):
                if past_msg["role"] == "user":
                    past_ram = IntentDetector.extract_ram(past_msg["content"])
                    if past_ram:
                        min_ram = past_ram
                        break

        # If product IDs missing for comparison, check recent history
        product_ids = slots.product_ids
        if slots.intent == UserIntent.COMPARISON and len(product_ids) < 2 and recent_history:
            for past_msg in reversed(recent_history):
                past_pids = IntentDetector.extract_product_ids(past_msg["content"])
                for pid in past_pids:
                    if pid not in product_ids:
                        product_ids.append(pid)
                if len(product_ids) >= 2:
                    break

        # 4. Intent-Based Routing
        products_out = []
        policy_faq_out = []
        sources = []
        lead_data = None
        assistant_answer = ""

        # --- A. Lead Capture Intent ---
        if slots.intent == UserIntent.LEAD_CAPTURE or slots.is_lead_candidate:
            lead_result = tools.capture_lead_tool(
                db=db,
                session_id=session_id,
                customer_name=slots.customer_name,
                email=slots.email,
                phone=slots.phone,
                budget_max=budget,
                preferred_ram=min_ram,
                purpose=slots.purpose,
                product_id=product_ids[0] if product_ids else None
            )
            lead_data = lead_result
            name_display = slots.customer_name or "sir/ma'am"
            contact_str = slots.phone or slots.email or "details"
            assistant_answer = (
                f"Thank you, {name_display}! Aapki contact information ({contact_str}) hamare sales executive ke "
                f"paas register ho gayi hai.\n\n"
                f"Hamari sales team aapko best price quotation aur doorstep delivery confirm karne ke liye turant connect karegi.\n"
                f"Is beech agar aapko warranty, payment modes ya specs ke regarding koi aur sawal hai, toh zaroor batayein!"
            )
            sources.append("lead_management_system")

        # --- B. Comparison Intent ---
        elif slots.intent == UserIntent.COMPARISON and len(product_ids) >= 2:
            comparison_data = tools.compare_products_tool(db, product_ids)
            products_out = comparison_data["products"]
            for p in products_out:
                sources.append(f"product_catalog_{p['product_id']}")

            if len(products_out) >= 2:
                p1, p2 = products_out[0], products_out[1]
                assistant_answer = (
                    f"**TechNova Comparison:**\n\n"
                    f"1. **{p1['name']}** (₹{p1['price']:,})\n"
                    f"   • Processor: {p1['processor']}\n"
                    f"   • RAM & Storage: {p1['ram_gb']}GB | {p1['storage']}\n"
                    f"   • Graphics: {p1['gpu']}\n"
                    f"   • Best For: {p1['suitable_for']}\n\n"
                    f"2. **{p2['name']}** (₹{p2['price']:,})\n"
                    f"   • Processor: {p2['processor']}\n"
                    f"   • RAM & Storage: {p2['ram_gb']}GB | {p2['storage']}\n"
                    f"   • Graphics: {p2['gpu']}\n"
                    f"   • Best For: {p2['suitable_for']}\n\n"
                    f"**Sales Verdict:** Agar aapka focus heavy multitasking aur budget par hai toh {p1['name']} great choice hai. "
                    f"Kya aap inme se kisi ek ke liye payment/EMI options dekhna chahenge?"
                )
            else:
                assistant_answer = "Mujhe comparison ke liye kam se kam 2 valid product models ki zaroorat hai. Kripya product names ya IDs mention karein."

        # --- C. Policy / FAQ Intent ---
        elif slots.intent == UserIntent.POLICY_FAQ:
            faq_chunks = tools.search_policy_faq_tool(query=message, top_k=2)
            policy_faq_out = faq_chunks
            for f in faq_chunks:
                sources.append(f.get("id", "company_policy_faq"))

            prompt = build_sales_rag_prompt(
                customer_query=message,
                retrieved_products=[],
                policy_faq_context=policy_faq_out,
                conversation_history=recent_history
            )
            assistant_answer = LLMGenerator.generate_response(prompt)

        # --- D. Product Recommendation / General Sales Inquiry ---
        else:
            retrieval = tools.search_catalog_tool(
                db=db,
                query=message,
                max_price=budget,
                min_ram=min_ram,
                brand=brand,
                top_k=3
            )
            products_out = retrieval["recommended_products"]
            policy_faq_out = retrieval["policy_and_faq_context"]
            sources.extend(retrieval["sources"])

            prompt = build_sales_rag_prompt(
                customer_query=message,
                retrieved_products=products_out,
                policy_faq_context=policy_faq_out,
                alternatives=retrieval.get("alternatives"),
                conversation_history=recent_history
            )
            assistant_answer = LLMGenerator.generate_response(prompt)

        # 5. Persist Multi-Turn Session History in SQLite
        crud.add_chat_message(db, session_id=session_id, role="user", content=message)
        crud.add_chat_message(db, session_id=session_id, role="assistant", content=assistant_answer)

        # 6. Return Structured Output
        return {
            "session_id": session_id,
            "message": message,
            "intent": slots.intent.value,
            "answer": assistant_answer,
            "recommended_products": products_out,
            "policy_and_faq_context": policy_faq_out,
            "lead_captured": lead_data,
            "sources": list(dict.fromkeys(sources))
        }
