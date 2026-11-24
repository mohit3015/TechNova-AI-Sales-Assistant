"""
=============================================================================
TechNova AI Sales Assistant - Text Cleaning & Normalization Utilities
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file raw documents ke text ko clean aur sanitize karti hai:
   1. `clean_text()`: Whitespace, carriage returns, unwanted unicode symbols normalize karta hai.
   2. `sanitize_metadata_value()`: Metadata values ko ChromaDB-compatible types (str, int, float, bool) mein convert karta hai.

🎯 USE CASE:
   Chunking aur embedding se pehle data cleaning ke liye.

🛠️ WHEN TO MODIFY THIS FILE:
   - Special characters, HTML tags ya custom formatting strip karne ke rules add karne hon.
=============================================================================
"""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace, strip control characters, and clean raw text."""
    if not text or not isinstance(text, str):
        return ""
    
    # Replace carriage returns and excessive whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and tabs
    text = text.replace("\u00a0", " ").replace("\t", " ")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ ]{2,}", " ", text)
    # Replace 3 or more newlines with double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_metadata_value(val):
    """Ensure metadata value is compatible with ChromaDB (str, int, float, bool)."""
    if val is None:
        return ""
    if isinstance(val, (int, float, bool)):
        return val
    return str(val).strip()
