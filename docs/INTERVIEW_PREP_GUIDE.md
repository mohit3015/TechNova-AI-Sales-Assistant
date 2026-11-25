# 💼 TechNova AI Sales Assistant — Complete Interview Master Guide
> **Comprehensive Zero-to-Hero Guide & Technical Interview Question Bank**  
> *Prepared for Mohit Kumar | AI/ML & GenAI Software Engineer*

---

## 📌 Table of Contents
1. [60-Second Elevator Pitch (Interview Intro)](#1-60-second-elevator-pitch)
2. [The Core Problem Statement](#2-the-core-problem-statement)
3. [System Architecture & End-to-End Workflow](#3-system-architecture--workflow)
4. [The 5 Core Technical Pillars (Deep Dive)](#4-the-5-core-technical-pillars)
   - [Pillar 1: Dual-Database Pattern (Anti-Hallucination)](#pillar-1-dual-database-anti-hallucination-architecture)
   - [Pillar 2: Hybrid Retrieval & Cross-Encoder Reranking](#pillar-2-hybrid-retrieval--cross-encoder-reranking)
   - [Pillar 3: Multi-Turn Memory & Smart Context Switching](#pillar-3-multi-turn-memory--smart-context-switching)
   - [Pillar 4: Intent Detection & Tool Orchestration](#pillar-4-intent-detection--tool-orchestration)
   - [Pillar 5: 25-Scenario Evaluation Suite & Metrics](#pillar-5-25-scenario-rag-evaluation-suite)
5. [Top 24 Technical Interview Questions & Answers](#5-top-24-technical-interview-questions--answers)
   - [Category A: High-Level Architecture & Design (Q1–Q5)](#category-a-architecture--design)
   - [Category B: RAG, Embeddings & Reranking (Q6–Q10)](#category-b-rag-embeddings--reranking)
   - [Category C: Agent Orchestration, Memory & State (Q11–Q14)](#category-c-agent-memory--state)
   - [Category D: Evaluation, Benchmarks & Metrics (Q15–Q18)](#category-d-evaluation--metrics)
   - [Category E: Production Readiness, Security & Docker (Q19–Q24)](#category-e-production-security--deployment)
6. [Quick Cheat Sheet: Numbers & Tech Stack](#6-quick-cheat-sheet)

---

## 1. 60-Second Elevator Pitch

Jab interviewer bole: **"Tell me about your TechNova AI Sales Assistant project"**, aapko ye bolna hai:

> *"TechNova AI Sales Assistant ek enterprise-grade GenAI application hai jise maine e-commerce aur laptop retail ke liye build kiya hai.*  
>  
> *Standard chatbots ki sabse badi problem hoti hai ki wo product prices aur hardware specs hallucinate kar dete hain, aur 2 turns ke baad customer ka budget bhool jaate hain. Isko solve karne ke liye maine ek **Dual-Database Architecture** design ki:*
> 1. *Authoritative **Relational SQLite database** for strictly deterministic data jaise exact prices (₹), live inventory count aur specs.*
> 2. ***ChromaDB Vector Store** with 384-dimensional dense embeddings for semantic search over unstructured company policies, return rules, and product suitability.*
>  
> *Pipeline mein **Hybrid Retrieval** ke baad maine **Cross-Encoder Reranking** lagaya hai to optimize candidate relevance. Chatbot mein **Multi-Turn Context Carryover** aur **CRM Lead Capture** built-in hai.*  
>  
> *Is project ko validate karne ke liye maine ek custom **25-Scenario Automated Evaluation Suite** likha hai jo **100% Price Accuracy** aur **100% Recall@K** verify karta hai with **~1,070 ms P50 latency**. Poora system **FastAPI** backend, **Streamlit** frontend aur **Docker persistent volumes** ke saath production-ready hai aur live deployed hai."*

---

## 2. The Core Problem Statement

Conventional retail chatbots mein 4 fatal flaws hote hain:
1. **Numerical Hallucination:** LLMs probability par kaam karte hain. Agar customer poochhe *"₹50k ke andar gaming laptop"*, LLM ₹65k ka laptop suggest karke uska price fake karke ₹48,000 likh deta hai. Retail mein ye legal aur business liability hai.
2. **Context Loss (Amnesia):** Turn 1: *"50 hazar ke andar laptop dikhao"* $\rightarrow$ Turn 2: *"isme se 16GB RAM kisme hai?"*. Most generic bots Turn 2 par budget bhool kar 1 lakh wale laptop recommend kar dete hain.
3. **Semantic Disconnect:** Vector similarity alone exact numerical constraints (jaise `price <= 50000`, `ram >= 16`) enforce nahi kar sakti.
4. **Lack of Sales Consultation:** Simple FAQ bot sirf information deta hai, closing questions pooch kar ya customer contact qualify karke CRM lead convert nahi karta.

---

## 3. The 5 Core Technical Pillars

### Pillar 1: Dual-Database Anti-Hallucination Architecture
* **Relational DB (SQLite):** Authoritative single source of truth for exact volatile fields: `price` (INR), `stock_count`, `ram_gb`, `product_id`.
* **Vector DB (ChromaDB):** Dense semantic representation of unstructured data: `policies.txt` (Warranty, 7-day replacement, No-cost EMI, Shipping), `faqs.json`, and hardware suitability summaries.
* **Anti-Hallucination Guarantee:** LLM prompt mein verified SQL output inject hota hai. LLM kabhi price guess nahi karta.

### Pillar 2: Hybrid Retrieval & Cross-Encoder Reranking
1. **SQL Filtering:** Candidate set matching hard constraints (`WHERE price <= budget AND ram_gb >= min_ram AND stock_count > 0`).
2. **Dense Vector Search:** ChromaDB cosine similarity search using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Cross-Encoder Reranking:** `cross-encoder/ms-marco-MiniLM-L-6-v2` query aur product description ko jointly cross-attention se score karta hai.
4. **Zero-Match Fallback:** Agar budget ke andar candidate 0 hon (e.g. 16GB RAM under ₹20,000), system smart Upselling aur Downselling calculate karta hai.

### Pillar 3: Multi-Turn Memory & Smart Context Switching
* SQLite `chat_history` table session persist karta hai.
* **Context Carryover:** User Turn 1 par budget bole aur Turn 2 par follow-up sawal poochhe, agent pichhla budget carry over karta hai.
* **Smart Reset Gate:** Agar user extreme keyword bole (*'sabse mehenga'*, *'cheapest'*) ya naya purpose maange (*'Machine Learning ke liye best laptop'* without pronouns), agent context carryover automatically bypass karta hai.

### Pillar 4: Intent Detection & Tool Orchestration
Regex + Semantic heuristics parser:
* `RECOMMENDATION`, `COMPARISON`, `POLICY_FAQ`, `LEAD_CAPTURE`, `GREETING`.
* Lead capture: Indian 10-digit mobile number (`[6-9]\d{9}`), email, customer name persist hota hai SQLite `leads` table mein.

### Pillar 5: 25-Scenario Evaluation Suite
Automated regression suite testing 25 diverse scenarios across 8 categories:
* **Retrieval Recall@K:** 100%
* **Price Accuracy Rate:** 100% (Strict comparison against SQL table)
* **Context Faithfulness Rate:** 92.0%
* **Answer Relevancy:** 100%
* **P50 Latency:** ~1,070 ms | **P90:** ~2,620 ms | **Average:** ~1,520 ms
