"""
=============================================================================
TechNova AI Sales Assistant - Universal LLM Response Generator
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file final natural language response generate karne ki responsible hai:
   1. Cloud LLM Integration: Agar `.env` mein key ho toh OpenRouter ya Groq API ko call karti hai.
   2. Deterministic Local Synthesizer: Agar API key na ho ya offline ho, tab bhi retrieved database context se high-quality, professional Hinglish/English sales response generate karti hai.

🎯 USE CASE:
   Sales Agent prompt taiyyar karke is generator ko call karta hai, aur yeh customer ke liye final answer return karta hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - LLM model (e.g. Llama-3, Mistral, Claude) change karna ho ya local synthesizer ka format customize karna ho.
=============================================================================
"""

from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.llm.prompts import TECHNOVA_SYSTEM_PROMPT


class LLMGenerator:
    """Universal LLM caller with support for OpenRouter, Groq, and fallback response synthesis."""

    @classmethod
    def generate_response(
        cls,
        prompt: str,
        system_prompt: str = TECHNOVA_SYSTEM_PROMPT,
        temperature: float = 0.3
    ) -> str:
        """Call external LLM API if key is available, else synthesize structured sales answer."""
        api_key = settings.OPENROUTER_API_KEY or settings.GROQ_API_KEY
        
        if api_key and api_key.strip():
            try:
                return cls._call_api(prompt, system_prompt, api_key, temperature)
            except Exception as e:
                print(f"[LLMGenerator] API call failed ({e}). Falling back to local synthesizer.")

        return cls._local_sales_synthesizer(prompt)

    @classmethod
    def _call_api(cls, prompt: str, system_prompt: str, api_key: str, temperature: float) -> str:
        """Call OpenAI-compatible endpoints (OpenRouter or Groq)."""
        if settings.LLM_PROVIDER.lower() == "groq" or (settings.GROQ_API_KEY and not settings.OPENROUTER_API_KEY):
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            model = settings.DEFAULT_LLM_MODEL if "llama" in settings.DEFAULT_LLM_MODEL else "llama-3.1-8b-instant"
        else:
            endpoint = "https://openrouter.ai/api/v1/chat/completions"
            model = settings.DEFAULT_LLM_MODEL

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if "openrouter" in endpoint:
            headers["HTTP-Referer"] = "https://technova.store"
            headers["X-Title"] = "TechNova AI Sales Assistant"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 700
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    @classmethod
    def _local_sales_synthesizer(cls, prompt: str) -> str:
        """High-quality grounded synthesizer that generates conversational sales responses
        without requiring external API credits.
        """
        # Parsing context sections from the prompt
        lines = prompt.split("\n")
        
        customer_query = ""
        for i, l in enumerate(lines):
            if l.startswith('Customer Inquiry:') and i + 1 < len(lines):
                customer_query = lines[i + 1].strip('"\t ')

        # Greeting detection
        lower_q = customer_query.lower()
        if any(w in lower_q for w in ["hello", "hi", "hey", "namaste"]) and len(lower_q.split()) <= 3:
            return (
                "Namaste! TechNova Store mein aapka swagat hai. \n\n"
                "Main aapka AI Sales Representative hoon. Main aapke budget aur requirements (jaise Coding, "
                "Machine Learning, Gaming, ya Daily Office use) ke hisaab se best laptop choose karne mein help karunga.\n\n"
                "Aapka approximate budget kitna hai aur aap laptop kis primary purpose ke liye search kar rahe hain?"
            )

        # Policy / FAQ query detection
        if any(w in lower_q for w in ["warranty", "return", "emi", "delivery", "shipping", "discount"]):
            if "Relevant Company Policies" in prompt:
                policies_section = prompt.split("Relevant Company Policies & FAQs:")[1].split("Customer Inquiry:")[0]
                return (
                    f"TechNova Store policies ke regarding aapki jankari:\n\n"
                    f"{policies_section.strip()}\n\n"
                    f"Kya aap kisi specific laptop model ki details ya live stock check karna chahenge?"
                )

        # Product Recommendation synthesis
        if "Authoritative Product Catalog" in prompt:
            catalog_section = prompt.split("Authoritative Product Catalog (Live Database):")[1]
            if "###" in catalog_section:
                catalog_section = catalog_section.split("###")[0]

            products_raw = [p.strip() for p in catalog_section.split("- Product:") if p.strip()]
            
            if products_raw:
                top_prod = products_raw[0]
                response_parts = [
                    "Aapki requirements ke according maine hamare live catalog se best options filter kiye hain:\n"
                ]

                # Format primary recommendation
                p_lines = top_prod.split("\n")
                name_line = p_lines[0].strip()
                response_parts.append(f" **Best Recommendation: {name_line}**")
                for pl in p_lines[1:]:
                    pl_clean = pl.strip()
                    if any(key in pl_clean for key in ["Price:", "RAM:", "Processor:", "Stock:", "Best For:"]):
                        response_parts.append(f"• {pl_clean}")

                # If there is a secondary option
                if len(products_raw) > 1:
                    second_prod = products_raw[1].split("\n")[0].strip()
                    price_line = [l.strip() for l in products_raw[1].split("\n") if "Price:" in l]
                    price_str = price_line[0] if price_line else ""
                    response_parts.append(f"\n **Alternative Option: {second_prod}** ({price_str})")

                response_parts.append(
                    "\n**Why this is recommended?**\n"
                    "Yeh laptop aapke budget ke andar best price-to-performance ratio provide karta hai aur "
                    "aapke mentioned workload ko smoothly handle karega.\n\n"
                    "TechNova Store offers **1-Year Warranty**, **7-Day Replacement Policy**, aur **Free 24-48 hr Delivery**.\n\n"
                    "Kya aap inka detailed comparison dekhna chahenge ya order reserve karne ke liye details share karna chahenge?"
                )
                return "\n".join(response_parts)

        # Alternative synthesis for zero-result scenario
        if "Alternative Options for Upselling" in prompt:
            alts_section = prompt.split("Alternative Options for Upselling / Budget Adjustment:")[1].split("###")[0]
            return (
                "Aapke exact specifications hamare current stock mein diye gaye budget ke andar match nahi huye, "
                "lekin ek sales representative ki tarah main aapke liye yeh best nearest options recommend karta hoon:\n\n"
                f"{alts_section.strip()}\n\n"
                "Aapki preference ke hisaab se kya aap budget thoda stretch karna chahenge ya alternative configuration choose karenge?"
            )

        return (
            "TechNova Store mein aapka swagat hai! Main aapko sahi laptop chunne mein madad kar sakta hoon.\n\n"
            "Kripya apna budget (e.g. ₹50,000) aur primary usage (Coding, Machine Learning, Gaming, Office) batayein, "
            "taaki main live database se best matching laptops suggest kar sakoon."
        )
