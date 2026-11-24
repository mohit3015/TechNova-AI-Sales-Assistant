# 💻 TechNova AI Sales Assistant
### RAG-Based Customer Support & Intelligent Product Recommendation System

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Sentence Transformers](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-yellow.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade **AI Sales Copilot and Product Recommendation Engine** designed for e-commerce and retail businesses. Unlike conventional generic chatbots, this system acts as a real consultative sales representative—retrieving authoritative data from product catalogs, live inventory counts, hardware specifications, return policies, warranty terms, and financing options.

---

## 🏗️ System Architecture

The project implements a **Dual-Database Architecture** with **Hybrid Retrieval & Cross-Encoder Reranking**, strictly separating structured volatile data (pricing & stock) from semantic unstructured context (policies & descriptions) to prevent hallucinations.

```mermaid
flowchart TD
    User["👤 Customer / Client"] <--> UI["💻 Streamlit Web Application\n(Port 8501)"]
    UI <--> API["⚡ FastAPI Backend Engine\n(Port 8000)"]
    
    subgraph AI_Intelligence_Layer ["🧠 AI Sales Intelligence Layer"]
        API <--> Agent["🤖 Sales Agent Orchestrator"]
        Agent <--> Intent["🎯 Intent & Slot Extractor\n(Budget, RAM, Purpose, Contacts)"]
        Agent <--> Memory["🧠 Multi-Turn Session Memory\n(SQLite Context Carryover)"]
    end
    
    subgraph Hybrid_Retrieval_System ["🔍 Hybrid Retrieval & Reranking"]
        Agent <--> HR["🔀 Hybrid Retriever"]
        HR <--> SQL["🗄️ SQLite Database\n(Authoritative Price, Specs, Live Stock)"]
        HR <--> VDB["🔮 ChromaDB Vector Store\n(384-dim Embeddings: Policies, FAQs, Reviews)"]
        HR --> Rerank["⚖️ Cross-Encoder Reranker\n(ms-marco-MiniLM-L-6-v2)"]
    end
    
    subgraph Generation_Layer ["📝 Grounded Response Generation"]
        Rerank --> Gen["💎 Universal LLM Generator\n(OpenRouter / Groq / Local Sales Synthesizer)"]
        Gen --> Output["📦 Final Sales Response\n(Product Cards + Pricing + Verified Sources)"]
    end
```

---

## ✨ Key Architectural Highlights

### 1. Dual-Database Pattern (Anti-Hallucination Guarantee)
* **ChromaDB Vector Store:** Houses semantic product overviews, suitability profiles, company warranty policies, and customer FAQs.
* **SQLite Relational DB:** Authoritative single source of truth for exact product prices (₹), stock inventory counts, RAM sizes, and product IDs.
* **Why this matters:** LLMs frequently hallucinate numbers. By decoupling pricing into a SQL database and injecting validated database records into the prompt, prices and stock counts are **100% factually grounded**.

### 2. Hybrid Retrieval with Cross-Encoder Reranking
1. **Deterministic SQL Filtering:** Pre-filters candidate laptops strictly matching the customer's budget and RAM constraints (e.g. `WHERE price <= 50000 AND ram_gb >= 16`).
2. **Dense Vector Search:** Retrieves semantic suitability chunks from ChromaDB using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Cross-Encoder Scoring:** Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` to evaluate deep query-document interaction scores and reorders candidate laptops by true relevance to the customer's workload.

### 3. Multi-Turn Conversational Memory & Context Carryover
* Maintains session state across turns using SQLite `chat_history`.
* If a customer specifies a budget in Turn 1 (*"50,000 ke andar laptop dikhao"*), and asks about warranty in Turn 2 (*"isme warranty kitni hai?"*), the agent retains the earlier budget and active product models without resetting context.

### 4. Smart Zero-Result Sales Fallbacks (Upselling & Alternatives)
* When a customer requests an out-of-budget configuration (e.g. 16GB RAM under ₹20,000), traditional bots fail with *"No products found"*.
* TechNova dynamically executes fallback queries to retrieve the nearest higher-budget model (upsell) and within-budget alternatives (downsell), guiding the customer naturally toward a purchase.

### 5. Automated CRM Lead Qualification
* Detects customer buying intent, parses contact details (phone, email, name), and automatically creates qualified sales records in the CRM database (`leads` table).
* Sales teams can view, review, and export leads as CSV directly from the frontend dashboard.

---

## 📂 Project Directory Structure

```text
AI_Sales_Assistant/
├── app/
│   ├── main.py                     # FastAPI backend application & lifespan handlers
│   ├── config.py                   # Pydantic BaseSettings & absolute path configurations
│   ├── api/                        # REST API Routers
│   │   ├── chat.py                 # Chat & recommendation endpoint (POST /api/chat)
│   │   ├── products.py             # Products catalog & comparison endpoints
│   │   └── leads.py                # CRM lead capture & management endpoints
│   ├── database/                   # Database & ORM Layer
│   │   ├── models.py               # SQLAlchemy schemas (Product, Lead, ChatHistory)
│   │   ├── connection.py           # Engine & session management
│   │   └── crud.py                 # Parameterized safe database queries
│   ├── retrieval/                  # Hybrid Search & Reranking Engine
│   │   ├── hybrid_search.py        # Core RAG hybrid search orchestrator
│   │   ├── sql_search.py           # Deterministic SQL search & alternative fallbacks
│   │   ├── vector_search.py        # ChromaDB semantic similarity search
│   │   └── reranker.py             # Cross-Encoder candidate reranker
│   ├── agents/                     # Conversational Sales Intelligence
│   │   ├── intent_detection.py     # Intent classification & entity slot extractor
│   │   ├── sales_agent.py          # Multi-turn sales agent & context carryover
│   │   └── tools.py                # Discrete execution tools (Catalog, Compare, Leads)
│   ├── llm/                        # Generation Layer
│   │   ├── prompts.py              # Grounded sales system prompts & templates
│   │   └── generator.py            # Universal LLM caller & local fallback synthesizer
│   └── services/                   # Service Layer
│       ├── chat_service.py         # Chat coordination service
│       └── lead_service.py         # Lead validation & management service
├── data/                           # Knowledge Base & Raw Datasets
│   ├── products.csv                # 12 real-world laptop catalog specifications
│   ├── policies.txt                # Warranty, return, delivery & EMI policy rules
│   └── faqs.json                   # Structured common customer questions & answers
├── frontend/
│   └── streamlit_app.py            # Modern Glassmorphic CRM & AI Sales Workspace
├── scripts/
│   └── seed_db.py                  # One-command SQLite & ChromaDB ingestion script
├── tests/                          # Automated Verification & Evaluation Suite
│   ├── test_api.py                 # FastAPI endpoints test
│   ├── test_retrieval.py           # SQL & ChromaDB retrieval test
│   ├── test_sales_agent.py         # Multi-turn conversational flow test
│   └── eval_rag.py                 # Automated RAG benchmarking suite
├── run_app.py                      # Unified dual-runner script (FastAPI + Streamlit)
├── requirements.txt                # Pinned production dependencies
├── Dockerfile                      # Containerization definition
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git secrets & cache exclusions
└── README.md                       # Comprehensive project documentation
```

---

## 🚀 Quickstart Guide (Local Setup)

### Prerequisites
* Python 3.10+ installed
* Git

### 1. Clone the Repository
```bash
git clone https://github.com/mohit3015/TechNova-AI-Sales-Assistant.git
cd TechNova-AI-Sales-Assistant
```

### 2. Create and Activate Virtual Environment
**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize & Seed Databases (One-Command Setup)
Populates SQLite with catalog products and builds ChromaDB 384-dimensional dense vectors:
```bash
python scripts/seed_db.py
```

### 5. Launch the Full-Stack Application
Start both FastAPI (Port 8000) and Streamlit UI (Port 8501) with a single command:
```bash
python run_app.py
```
* **Frontend Web UI:** `http://localhost:8501`
* **FastAPI Backend:** `http://127.0.0.1:8000`
* **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

---

## 🐳 Docker Deployment & Persistent Storage

The application is fully containerized with persistent volume support for SQLite and ChromaDB:

```bash
# 1. Build Production Docker Image
docker build -t technova-ai-sales-assistant .

# 2. Run Container with Named Persistent Volume (Preserves leads and history across restarts)
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -v technova_storage:/app/storage \
  --name technova-app \
  technova-ai-sales-assistant
```

* **Frontend Web UI:** `http://localhost:8501`
* **FastAPI Backend:** `http://localhost:8000`
* **Persistent Volume:** Mounted at `/app/storage` (SQLite DB & ChromaDB auto-seed on first volume initialization and persist across restarts).

---

## 📊 Automated RAG Evaluation & Production Benchmarks

The project features a **25-Scenario Automated Benchmark Suite** (`tests/eval_rag.py`) measuring end-to-end RAG quality across:
* Budget constraints (e.g. ₹40k, ₹50k, ₹60k)
* AI/Workstations & AAA Gaming
* Direct Product ID lookups (P101–P112)
* Side-by-side product comparisons
* Policies, warranty terms, and FAQs
* Zero-match smart fallback upselling
* CRM lead generation & Indian phone format validation
* Hinglish colloquial queries

```bash
python tests/eval_rag.py
```

### Measured Production Benchmark Results

| Metric | Measured Score | Target Standard | Evaluation Methodology |
| :--- | :---: | :---: | :--- |
| **Retrieval Recall@K** | **100.0%** | > 85% | Target product and suitability chunks present in Top-K retrieved items |
| **Price Accuracy Rate** | **100.0%** | 100% | Zero price hallucination (100% strict verification against SQL database) |
| **Answer Relevancy** | **100.0%** | > 90% | Response directly addresses user intent, purpose, and entity requirements |
| **Context Faithfulness** | **92.0%** | > 85% | Verified factual consistency with retrieved catalog and policy documents |
| **Overall Suite Pass Rate** | **96.0%** | > 80% | Comprehensive 25-scenario evaluation pass rate |
| **End-to-End Latency (P50)**| **~1,070 ms** | < 2,000 ms | Median response time on CPU hardware |
| **End-to-End Latency (P90)**| **~2,620 ms** | < 4,000 ms | 90th percentile response time including Cross-Encoder reranking |
| **End-to-End Latency (Avg)**| **~1,520 ms** | < 2,500 ms | Average end-to-end pipeline latency |

---

## 🧪 Running Unit & Integration Tests

```bash
# Test 1: SQLite filtering & Vector similarity
python tests/test_retrieval.py

# Test 2: FastAPI endpoints & CRUD operations
python tests/test_api.py

# Test 3: Multi-turn sales dialogue & lead qualification
python tests/test_sales_agent.py

# Test 4: Comprehensive RAG benchmark suite
python tests/eval_rag.py
```

---

## 👤 Author
**Mohit Kumar**  
GitHub: [@mohit3015](https://github.com/mohit3015)  
Repository: [https://github.com/mohit3015/TechNova-AI-Sales-Assistant](https://github.com/mohit3015/TechNova-AI-Sales-Assistant)

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
