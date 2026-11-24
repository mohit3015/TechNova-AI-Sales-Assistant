"""
=============================================================================
TechNova AI Sales Assistant - System Prompts & Grounding Templates
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file AI Chatbot ki "Personality", "Sales Tone" aur "Grounding Rules" define karti hai:
   1. Factual Grounding: LLM ko strictly instruct karta hai ki sirf retrieved context se answer de (No Price/Specs invention).
   2. Consultative Approach: Sirf specs list na kare, balki explain kare ki laptop user ke purpose (Python, Gaming, Office) ke liye kyun best hai.
   3. Closing Questions: Follow-up question pooch kar conversation ko deal booking ki taraf guide karta hai.

🎯 USE CASE:
   `sales_agent.py` is file se prompt builder function (`build_sales_rag_prompt`) call karke
   retrieved database context aur customer question ko ek formatted prompt mein assemble karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Chatbot ke sales guidelines, discounts offer, ya tone of voice (English vs Hinglish) change karne ke liye.
=============================================================================
"""

TECHNOVA_SYSTEM_PROMPT = """You are the Senior AI Sales Representative for TechNova Store — a premier laptop and technology retailer.
Your mission is to guide customers seamlessly from initial product discovery to confident purchase decisions.

### CRITICAL GROUNDING & SALES RULES:
1. FACTUAL GROUNDING: Rely strictly on the provided context (retrieved products, specifications, pricing, policies, and FAQs). NEVER invent, guess, or modify product prices, hardware specs, or stock availability.
2. PRICE CLARITY: Always quote prices clearly in Indian Rupees (e.g. ₹42,999).
3. CONSULTATIVE SALES APPROACH:
   - Don't just list specs; explain WHY a particular laptop matches the customer's stated needs (e.g., "Ryzen 5 with 16GB RAM handles Python multiprocessing and IDEs smoothly").
   - If multiple laptops are retrieved, recommend the single best fit as the primary choice, followed by 1 alternative.
4. OUT-OF-BUDGET / ZERO MATCH HANDLING:
   - If the customer asks for a configuration not possible within their budget, politely inform them, then present the nearest alternatives provided in context.
5. CONVERSATIONAL CLOSING:
   - End with a polite, relevant follow-up question that advances the conversation (e.g., asking if they want a side-by-side spec comparison, EMI details, or would like to reserve a unit).
6. LANGUAGE: Match the customer's conversational style (fluent natural Hinglish or professional English). Keep explanations crisp, friendly, and structured.
"""


def build_sales_rag_prompt(
    customer_query: str,
    retrieved_products: list,
    policy_faq_context: list,
    alternatives: dict = None,
    conversation_history: list = None
) -> str:
    """Constructs the prompt fed into the LLM generator with all grounded context."""
    context_sections = []

    # 1. Conversation History (if multi-turn)
    if conversation_history:
        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
        context_sections.append(f"### Recent Conversation History:\n{history_text}")

    # 2. Authoritative Product Information
    if retrieved_products:
        prod_text = []
        for p in retrieved_products:
            prod_text.append(
                f"- Product: {p['name']} (ID: {p['product_id']})\n"
                f"  Price: ₹{p['price']:,} | RAM: {p['ram_gb']}GB | Storage: {p['storage']}\n"
                f"  Processor: {p['processor']} | GPU: {p['gpu']} | Display: {p['display']}\n"
                f"  Stock: {p['stock_count']} units available | Warranty: {p['warranty_years']} Year(s)\n"
                f"  Best For: {p['suitable_for']}\n"
                f"  Overview: {p.get('suitability_reason', p.get('description', ''))}"
            )
        context_sections.append(f"### Authoritative Product Catalog (Live Database):\n" + "\n\n".join(prod_text))

    # 3. Alternatives (if zero-match or upsell/downsell available)
    if alternatives:
        alt_text = []
        if alternatives.get("higher_budget_options"):
            for a in alternatives["higher_budget_options"]:
                alt_text.append(f"  • Higher Budget Option: {a['name']} (₹{a['price']:,}, {a['ram_gb']}GB RAM)")
        if alternatives.get("budget_friendly_options"):
            for a in alternatives["budget_friendly_options"]:
                alt_text.append(f"  • Within-Budget Alternative: {a['name']} (₹{a['price']:,}, {a['ram_gb']}GB RAM)")
        if alt_text:
            context_sections.append("### Alternative Options for Upselling / Budget Adjustment:\n" + "\n".join(alt_text))

    # 4. Relevant Policies & FAQs
    if policy_faq_context:
        pf_text = [f"- {item['content']}" for item in policy_faq_context]
        context_sections.append("### Relevant Company Policies & FAQs:\n" + "\n".join(pf_text))

    full_context = "\n\n".join(context_sections)

    return f"""Context Information:
{full_context}

Customer Inquiry:
"{customer_query}"

Provide your professional sales response according to the TechNova guidelines."""
