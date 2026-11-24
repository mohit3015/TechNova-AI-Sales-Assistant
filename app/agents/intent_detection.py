"""
=============================================================================
TechNova AI Sales Assistant - Intent Detection & Entity Slot Extractor
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file customer ke natural language message ko analyze karke uski intent aur requirements extract karti hai:
   1. User Intent: `recommendation`, `comparison`, `policy_faq`, `lead_capture`, `greeting`.
   2. Extracted Slots:
      - Budget: Extracts ₹50,000, 50k, 4 lakhs, under 60k.
      - RAM: Extracts 8GB, 16GB, 32GB.
      - Purpose: Coding, Machine Learning, Gaming, Video Editing, Office.
      - Contact Info: Phone number, email address, customer name.
      - Product IDs: P101, P103, P104.

🎯 USE CASE:
   Sales Agent ka first step hota hai user ke message ko parse karna taaki pata chale ki SQL/Chroma mein kya dhoondhna hai.

🛠️ WHEN TO MODIFY THIS FILE:
   - Agar naye keywords, naye intents, ya naye budget patterns support karne hon.
=============================================================================
"""

import re
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class UserIntent(str, Enum):
    RECOMMENDATION = "recommendation"
    COMPARISON = "comparison"
    POLICY_FAQ = "policy_faq"
    LEAD_CAPTURE = "lead_capture"
    GREETING = "greeting"
    GENERAL = "general"


class ExtractedSlots(BaseModel):
    intent: UserIntent = UserIntent.GENERAL
    budget_max: Optional[int] = None
    min_ram: Optional[int] = None
    purpose: Optional[str] = None
    brand: Optional[str] = None
    product_ids: List[str] = []
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_lead_candidate: bool = False


class IntentDetector:
    """Robust, deterministic intent detection and entity slot extractor."""

    @staticmethod
    def extract_budget(text: str) -> Optional[int]:
        """Extracts maximum budget from phrases like 'under 50k', '50,000 ke andar', '₹45000', '4 lakhs'."""
        text_lower = text.lower().replace(",", "")
        
        # Match '4 lakh', '4 lakhs', '2 lac', '1.5 lakh', '6 lakh tak', '3 lakh mein'
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh[s]?|lac[s]?)\b", text_lower)
        if lakh_match:
            try:
                return int(float(lakh_match.group(1)) * 100000)
            except ValueError:
                pass

        # Match '50k', '60 k'
        k_match = re.search(r"(\d+)\s*k\b", text_lower)
        if k_match:
            try:
                return int(k_match.group(1)) * 1000
            except ValueError:
                pass

        # Match '50 hazar' or '50 hazaar'
        hazar_match = re.search(r"(\d+)\s*haza?ar\b", text_lower)
        if hazar_match:
            try:
                return int(hazar_match.group(1)) * 1000
            except ValueError:
                pass

        # Match numbers with 'under', 'below', 'budget', '₹', 'rs'
        budget_pattern = re.search(r"(?:under|below|budget|max|approx|upto|₹|rs\.?)\s*(\d{4,7})", text_lower)
        if budget_pattern:
            try:
                return int(budget_pattern.group(1))
            except ValueError:
                pass

        # Match standalone 5 to 7 digit number (e.g. 50000, 45000, 75000, 400000)
        digits_match = re.search(r"\b(\d{5,7})\b", text_lower)
        if digits_match:
            try:
                val = int(digits_match.group(1))
                if 15000 <= val <= 2000000:
                    return val
            except ValueError:
                pass

        return None

    @staticmethod
    def extract_ram(text: str) -> Optional[int]:
        """Extracts desired RAM size (e.g. 8gb, 16 gb, 32gb)."""
        ram_match = re.search(r"(\d{1,2})\s*(?:gb|gig)\s*(?:ram)?", text.lower())
        if ram_match:
            try:
                ram_val = int(ram_match.group(1))
                if ram_val in (4, 8, 16, 24, 32, 64):
                    return ram_val
            except ValueError:
                pass
        return None

    @staticmethod
    def extract_purpose(text: str) -> Optional[str]:
        """Identifies computing purpose using precise word boundary matching."""
        lower = text.lower()
        purposes = []
        if any(w in lower for w in ["machine learning", "deep learning", "datascience", "data science"]) or re.search(r"\b(ai|ml)\b", lower):
            purposes.append("Machine Learning & AI")
        if any(w in lower for w in ["coding", "programming", "python", "developer", "development", "web dev", "software"]):
            purposes.append("Programming & Development")
        if re.search(r"\b(gaming|games?|gta|fps)\b", lower):
            purposes.append("Gaming")
        if any(w in lower for w in ["video editing", "editing", "blender", "rendering", "graphic"]):
            purposes.append("Creative & Video Editing")
        if any(w in lower for w in ["student", "college", "school", "study", "studies"]):
            purposes.append("Students & Academics")
        if any(w in lower for w in ["office", "excel", "accounting", "business"]) or re.search(r"\b(work)\b", lower):
            purposes.append("Office & Business")

        return ", ".join(purposes) if purposes else None

    @staticmethod
    def extract_product_ids(text: str) -> List[str]:
        """Extracts TechNova product IDs (e.g. P101, P103, P110)."""
        matches = re.findall(r"\b(P\d{3})\b", text.upper())
        return list(dict.fromkeys(matches))

    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
        """Extracts customer phone number and email address."""
        # Phone: 10-digit Indian phone number
        phone = None
        phone_match = re.search(r"(?:(?:\+91|0)?[\s-]?)?([6-9]\d{9})\b", text)
        if phone_match:
            phone = phone_match.group(1)

        # Email
        email = None
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        if email_match:
            email = email_match.group(0)

        # Name heuristic (e.g. 'Mera naam Rahul', 'Name is Rohan', 'I am Priya')
        name = None
        name_match = re.search(r"(?:mera naam|name is|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).title()

        return {"phone": phone, "email": email, "name": name}

    @classmethod
    def detect(cls, text: str) -> ExtractedSlots:
        """Classify message intent and extract all relevant conversational slots."""
        lower = text.lower().strip()
        
        # 1. Contact / Lead Intent
        contacts = cls.extract_contact_info(text)
        is_lead = bool(contacts["phone"] or contacts["email"] or any(w in lower for w in ["buy karna hai", "kharidna hai", "purchase karna", "order book", "contact me"]))
        
        # 2. Product IDs & Comparison Intent
        pids = cls.extract_product_ids(text)
        is_compare = any(w in lower for w in ["compare", "vs", "versus", "comparison", "farak", "difference"]) or (len(pids) >= 2)

        # 3. Policy & FAQ Intent
        is_policy_faq = any(w in lower for w in [
            "warranty", "guarantee", "return", "refund", "replace", "replacement",
            "emi", "installment", "no cost emi", "delivery", "shipping", "deliver",
            "exchange", "discount", "offer", "student discount", "service center"
        ])

        # 4. Greeting Intent
        is_greeting = bool(re.search(r"^(hi+|hey+|hello+|namaste|hlo|good\s*(morning|evening|afternoon))\b", lower)) and len(lower.split()) <= 4

        # 5. Slots
        budget = cls.extract_budget(text)
        ram = cls.extract_ram(text)
        purpose = cls.extract_purpose(text)

        # 6. Catalog / List / Price query detection
        is_catalog_query = any(w in lower for w in [
            "list", "sab", "sabhi", "all laptop", "dikho", "dikhao", "show",
            "highest price", "sabse mahanga", "most expensive", "sabse sasta",
            "cheapest", "lowest price", "top laptop", "premium", "costly",
            "kitne laptop", "how many", "catalog"
        ])

        # Decision Logic
        if is_lead:
            intent = UserIntent.LEAD_CAPTURE
        elif is_compare:
            intent = UserIntent.COMPARISON
        elif is_policy_faq:
            intent = UserIntent.POLICY_FAQ
        elif budget or ram or purpose or is_catalog_query or any(w in lower for w in [
            "laptop", "suggest", "chahiye", "recommend", "options", "best",
            "kaun sa", "konsa", "which", "good", "acha"
        ]):
            intent = UserIntent.RECOMMENDATION
        elif is_greeting:
            intent = UserIntent.GREETING
        else:
            intent = UserIntent.GENERAL

        return ExtractedSlots(
            intent=intent,
            budget_max=budget,
            min_ram=ram,
            purpose=purpose,
            product_ids=pids,
            customer_name=contacts["name"],
            phone=contacts["phone"],
            email=contacts["email"],
            is_lead_candidate=is_lead
        )
