"""
=============================================================================
TechNova AI Sales Assistant - Frontend Web Application (Streamlit)
=============================================================================
📌 ROLE & PURPOSE:
   Yeh file hamare project ka complete User Interface (Frontend) hai.
   Isme ek modern, glassmorphic CRM & AI Sales Copilot Dashboard design kiya gaya hai:
   1. 💬 AI Sales Copilot: Clean chat interface, grounded product cards aur sources.
   2. 📊 Catalog & Comparison: Live inventory table, search filters aur 2 laptops ka comparison tool.
   3. 📝 CRM Leads Desk: Customer callback request form aur live leads table (CSV export ke saath).

🎯 USE CASE:
   Jab bhi user browser mein `http://localhost:8501` open karta hai, yeh file run hoti hai.
   Yeh FastAPI backend (`http://127.0.0.1:8000`) ko HTTP requests bhej kar data lati hai.

🔗 CONNECTIONS:
   - FastAPI Endpoints: `/health`, `/api/chat`, `/api/products`, `/api/leads`.

🛠️ WHEN TO MODIFY THIS FILE:
   - Agar UI colors, buttons, CSS styling ya text badalna ho.
   - Agar chat cards mein koi naya feature ya tab add/remove karna ho.
=============================================================================
"""

import uuid
import requests
import pandas as pd
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="TechNova | CRM & AI Sales Workspace",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000"

# --- Premium Executive Styling (Inspired by Modern CRM & AI Integration) ---
st.markdown("""
<style>
    /* Google Fonts & Body */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Brand Bar */
    .top-brand-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    /* Metric KPI Cards (Dark Mode Compatible) */
    .kpi-container {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }
    .kpi-card {
        flex: 1;
        background: #1e293b;
        border-radius: 16px;
        padding: 16px 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
        color: #f8fafc;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    .kpi-card.green::after { background: #10b981; }
    .kpi-card.blue::after { background: #0ea5e9; }
    .kpi-card.amber::after { background: #f59e0b; }
    .kpi-card.purple::after { background: #8b5cf6; }
    
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #10b981;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Product Card Styling (High Contrast & Dark Mode Friendly) */
    .product-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: #f8fafc !important;
    }
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
        border-color: #64748b;
    }
    .product-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 6px;
    }
    .price-tag {
        font-size: 1.4rem;
        font-weight: 800;
        color: #34d399 !important;
        margin-bottom: 12px;
    }
    .product-card p {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    .product-card b {
        color: #ffffff !important;
    }
    .spec-pill {
        display: inline-flex;
        align-items: center;
        background: #334155;
        color: #f1f5f9;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px 2px;
    }
    .badge-stock {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-warranty {
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid #0284c7;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .verdict-box {
        background: #0f172a;
        border: 1px solid #3b82f6;
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 15px;
        color: #f8fafc;
    }

    /* Custom Chat Styling */
    .stChatMessage {
        border-radius: 16px;
        padding: 12px 18px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions for API Communication ---

@st.cache_data(ttl=10)
def fetch_health():
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=10)
def fetch_products():
    try:
        res = requests.get(f"{API_BASE_URL}/api/products?limit=50", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=5)
def fetch_leads():
    try:
        res = requests.get(f"{API_BASE_URL}/api/leads?limit=50", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def send_chat_message(session_id: str, message: str, max_price=None, min_ram=None, brand=None):
    payload = {
        "session_id": session_id,
        "message": message,
        "max_price": max_price,
        "min_ram": min_ram,
        "brand": brand
    }
    try:
        response = requests.post(f"{API_BASE_URL}/api/chat", json=payload, timeout=30.0)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error ({response.status_code}): {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "FastAPI backend is offline. Run: `uvicorn app.main:app --reload --port 8000`"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def submit_lead(session_id, name, phone, email, notes, product_id=None):
    payload = {
        "session_id": session_id,
        "customer_name": name,
        "phone": phone,
        "email": email,
        "notes": notes,
        "interested_product_id": product_id
    }
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads", json=payload, timeout=5.0)
        return res.status_code == 201
    except Exception:
        return False


# --- Session State Setup ---

if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Namaste! **TechNova Store** mein aapka swagat hai. 💻✨\n\n"
                "Main aapka **AI Sales Assistant** hoon. Main aapke budget aur needs (Coding, Machine Learning, "
                "Gaming, ya Office Work) ke according live catalog se best laptop recommend karunga.\n\n"
                "Aapka approximate budget kitna hai aur laptop kis primary purpose ke liye search kar rahe hain?"
            ),
            "products": []
        }
    ]


# --- Top Header Bar ---

health_data = fetch_health()
is_online = health_data is not None and health_data.get("status") == "healthy"
chunk_count = health_data.get("vector_database", {}).get("indexed_chunks", 0) if health_data else 0

st.markdown(f"""
<div class="top-brand-bar">
    <div>
        <div class="brand-title">
            <span>💻</span> TechNova Store · AI Sales & CRM Workspace
        </div>
        <div class="brand-subtitle">
            Enterprise RAG Architecture · ChromaDB Vector Search · Real-Time Inventory Grounding
        </div>
    </div>
    <div>
        <span style="background: {'#10b981' if is_online else '#ef4444'}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700;">
            {'● Live API Connected' if is_online else '○ Backend Disconnected'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# --- KPI Summary Metric Cards (Inspired by Reference Design) ---

all_products = fetch_products()
all_leads = fetch_leads()

total_models = len(all_products)
total_stock = sum(p.get("stock_count", 0) for p in all_products)
leads_count = len(all_leads)
starting_price = min((p.get("price", 0) for p in all_products), default=28999)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-label">Active Catalog</div>
        <div class="kpi-value">{total_models} Models</div>
        <div class="kpi-sub">✓ Live in SQL DB</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-label">Total Inventory</div>
        <div class="kpi-value">{total_stock} Units</div>
        <div class="kpi-sub">📦 Available in Stock</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div class="kpi-label">ChromaDB Vectors</div>
        <div class="kpi-value">{chunk_count} Chunks</div>
        <div class="kpi-sub">⚡ 384-dim Embeddings</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div class="kpi-label">CRM Leads Captured</div>
        <div class="kpi-value">{leads_count} Leads</div>
        <div class="kpi-sub">🎯 Qualified Customers</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# --- Main Tabbed Layout (Executive Workspace) ---

tab_chat, tab_catalog, tab_leads = st.tabs([
    "💬 AI Sales Copilot",
    "📊 Catalog & Specs Comparison",
    "📝 CRM Leads & Reservation Desk"
])


# ==========================================
# TAB 1: AI SALES COPILOT (Chat Interface)
# ==========================================

with tab_chat:
    # Sidebar quick filters for this tab
    with st.sidebar:
        st.subheader("⚙️ Session Controls")
        st.code(st.session_state.session_id, language="text")
        if st.button("🔄 New Chat / Reset Memory", use_container_width=True):
            st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Namaste! New chat session initialized. Kripya apna budget aur use-case batayein.",
                    "products": []
                }
            ]
            st.rerun()

        st.divider()
        st.subheader("🎯 Guided Search Filters (Optional)")
        apply_filters = st.checkbox("Enforce Sidebar Constraints", value=False)
        sidebar_budget = None
        sidebar_ram = None
        if apply_filters:
            sidebar_budget = st.slider("Max Budget (₹)", 25000, 150000, 60000, 5000, format="₹%d")
            ram_opt = st.selectbox("Minimum RAM", ["Any", "8 GB", "16 GB", "32 GB"], index=2)
            if ram_opt != "Any":
                sidebar_ram = int(ram_opt.split()[0])

        st.divider()
        st.subheader("💡 Quick Prompts")
        quick_prompts = [
            "₹50,000 ke andar 16GB RAM coding laptop suggest karo",
            "Machine Learning aur Deep Learning ke liye best laptop kaun sa hai?",
            "P103 aur P104 ko compare karke difference batao",
            "TechNova warranty aur return policy kya hai?",
            "No-Cost EMI aur student discount available hai?"
        ]
        for qp in quick_prompts:
            if st.button(qp, key=f"btn_{qp[:12]}", use_container_width=True):
                st.session_state.prefill_query = qp
                st.rerun()

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="💻" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

            # Recommended Product Cards
            products = msg.get("products", [])
            if products:
                st.markdown("#### 🛍️ Recommended Laptops Matching Your Requirements")
                pcols = st.columns(min(len(products), 3))
                for i, prod in enumerate(products[:3]):
                    with pcols[i % 3]:
                        st.markdown(f"""
                        <div class="product-card">
                            <div>
                                <div class="product-title">{prod.get('name', 'Laptop')}</div>
                                <div class="price-tag">₹{prod.get('price', 0):,}</div>
                                <div>
                                    <span class="spec-pill">⚡ {prod.get('processor', 'CPU')}</span>
                                    <span class="spec-pill">💾 {prod.get('ram_gb', 0)}GB RAM</span>
                                    <span class="spec-pill">🎮 {prod.get('gpu', 'Integrated')}</span>
                                    <span class="spec-pill">🖥️ {prod.get('display', 'FHD')}</span>
                                </div>
                            </div>
                            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px dashed #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                                <span class="badge-stock">📦 Stock: {prod.get('stock_count', 0)}</span>
                                <span class="badge-warranty">🛡️ {prod.get('warranty_years', 1)} Yr Warranty</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Sources attribution expander
            sources = msg.get("sources", [])
            if sources:
                with st.expander("🔍 Verified Grounding Sources"):
                    st.caption(f"Factual data grounded on: `{', '.join(sources)}`")

    # Handle quick prompt selection
    active_query = None
    if "prefill_query" in st.session_state:
        active_query = st.session_state.pop("prefill_query")

    # Clean Chat Input at the very bottom
    user_msg = st.chat_input("Poochiye: e.g. ₹50,000 ke andar coding laptop suggest karo...") or active_query

    if user_msg:
        # Display user turn
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_msg)

        # Call API
        with st.chat_message("assistant", avatar="💻"):
            with st.spinner("TechNova database search ho raha hai..."):
                response = send_chat_message(
                    session_id=st.session_state.session_id,
                    message=user_msg,
                    max_price=sidebar_budget if apply_filters else None,
                    min_ram=sidebar_ram if apply_filters else None
                )

            if "error" in response:
                st.error(f"⚠️ {response['error']}")
                st.session_state.messages.append({"role": "assistant", "content": response["error"], "products": []})
            else:
                answer = response.get("answer", "")
                recs = response.get("recommended_products", [])
                srcs = response.get("sources", [])

                st.markdown(answer)

                if recs:
                    st.markdown("#### 🛍️ Recommended Laptops Matching Your Requirements")
                    pcols = st.columns(min(len(recs), 3))
                    for i, prod in enumerate(recs[:3]):
                        with pcols[i % 3]:
                            st.markdown(f"""
                            <div class="product-card">
                                <div>
                                    <div class="product-title">{prod.get('name', 'Laptop')}</div>
                                    <div class="price-tag">₹{prod.get('price', 0):,}</div>
                                    <div>
                                        <span class="spec-pill">⚡ {prod.get('processor', 'CPU')}</span>
                                        <span class="spec-pill">💾 {prod.get('ram_gb', 0)}GB RAM</span>
                                        <span class="spec-pill">🎮 {prod.get('gpu', 'Integrated')}</span>
                                        <span class="spec-pill">🖥️ {prod.get('display', 'FHD')}</span>
                                    </div>
                                </div>
                                <div style="margin-top: 14px; padding-top: 10px; border-top: 1px dashed #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                                    <span class="badge-stock">📦 Stock: {prod.get('stock_count', 0)}</span>
                                    <span class="badge-warranty">🛡️ {prod.get('warranty_years', 1)} Yr Warranty</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "products": recs,
                    "sources": srcs
                })

                if response.get("lead_captured"):
                    lead = response["lead_captured"]
                    st.success(f"🎉 Lead Captured: {lead.get('customer_name') or 'Customer'} ({lead.get('phone')})")

        st.rerun()


# ==========================================
# TAB 2: CATALOG & COMPARISON DASHBOARD
# ==========================================

with tab_catalog:
    st.subheader("📊 Live Product Catalog & Specification Matrix")
    st.caption("Authoritative SQL database view with real-time hardware specs, pricing, and live inventory.")

    if all_products:
        df = pd.DataFrame(all_products)
        display_cols = ["product_id", "name", "price", "ram_gb", "processor", "gpu", "storage", "stock_count", "warranty_years"]
        
        # Interactive Search Filter
        col_search, col_sort = st.columns([3, 1])
        with col_search:
            search_term = st.text_input("🔍 Search Catalog (e.g. RTX, Ryzen, 16GB, Coding)", placeholder="Filter laptops...")
        with col_sort:
            sort_by = st.selectbox("Sort By", ["Price (Low to High)", "Price (High to Low)", "RAM (High to Low)"])

        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search_term, case=False, na=False) |
                filtered_df["processor"].str.contains(search_term, case=False, na=False) |
                filtered_df["gpu"].str.contains(search_term, case=False, na=False) |
                filtered_df["suitable_for"].str.contains(search_term, case=False, na=False)
            ]

        if sort_by == "Price (Low to High)":
            filtered_df = filtered_df.sort_values(by="price", ascending=True)
        elif sort_by == "Price (High to Low)":
            filtered_df = filtered_df.sort_values(by="price", ascending=False)
        else:
            filtered_df = filtered_df.sort_values(by="ram_gb", ascending=False)

        # Format price with currency symbol
        formatted_df = filtered_df[display_cols].copy()
        formatted_df["price"] = formatted_df["price"].apply(lambda x: f"₹{x:,}")
        formatted_df.columns = ["ID", "Laptop Name", "Price", "RAM (GB)", "Processor", "GPU", "Storage", "Stock", "Warranty (Yrs)"]

        st.dataframe(formatted_df, use_container_width=True, hide_index=True)

        st.divider()

        # Side-by-Side Model Comparison Tool
        st.subheader("⚖️ Side-by-Side Laptop Comparison")
        comp_col1, comp_col2 = st.columns(2)
        model_names = [f"{p['product_id']} - {p['name']} (₹{p['price']:,})" for p in all_products]
        
        with comp_col1:
            sel_1 = st.selectbox("Select First Laptop", model_names, index=2 if len(model_names) > 2 else 0)
        with comp_col2:
            sel_2 = st.selectbox("Select Second Laptop", model_names, index=3 if len(model_names) > 3 else 1)

        pid_1 = sel_1.split()[0]
        pid_2 = sel_2.split()[0]

        prod_1 = next((p for p in all_products if p["product_id"] == pid_1), None)
        prod_2 = next((p for p in all_products if p["product_id"] == pid_2), None)

        if prod_1 and prod_2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">{prod_1['name']}</div>
                    <div class="price-tag">₹{prod_1['price']:,}</div>
                    <p><b>Processor:</b> {prod_1['processor']}</p>
                    <p><b>RAM & Storage:</b> {prod_1['ram_gb']}GB | {prod_1['storage']}</p>
                    <p><b>Graphics:</b> {prod_1['gpu']}</p>
                    <p><b>Display:</b> {prod_1['display']}</p>
                    <p><b>Battery Life:</b> {prod_1.get('battery_life_hours', 'N/A')} Hours | <b>Weight:</b> {prod_1.get('weight_kg', 'N/A')} kg</p>
                    <p><b>Ideal For:</b> {prod_1['suitable_for']}</p>
                    <p><b>Stock Available:</b> <span class="badge-stock">{prod_1['stock_count']} units</span></p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">{prod_2['name']}</div>
                    <div class="price-tag">₹{prod_2['price']:,}</div>
                    <p><b>Processor:</b> {prod_2['processor']}</p>
                    <p><b>RAM & Storage:</b> {prod_2['ram_gb']}GB | {prod_2['storage']}</p>
                    <p><b>Graphics:</b> {prod_2['gpu']}</p>
                    <p><b>Display:</b> {prod_2['display']}</p>
                    <p><b>Battery Life:</b> {prod_2.get('battery_life_hours', 'N/A')} Hours | <b>Weight:</b> {prod_2.get('weight_kg', 'N/A')} kg</p>
                    <p><b>Ideal For:</b> {prod_2['suitable_for']}</p>
                    <p><b>Stock Available:</b> <span class="badge-stock">{prod_2['stock_count']} units</span></p>
                </div>
                """, unsafe_allow_html=True)

            # Centered Action Button below the two comparison cards
            st.write("")
            b_c1, b_c2, b_c3 = st.columns([1, 2, 1])
            with b_c2:
                compare_btn = st.button("⚡ Compare Specifications with AI Assistant", key="btn_compare_center", type="primary", use_container_width=True)

            if compare_btn:
                # Calculate differences
                price_diff = abs(prod_1['price'] - prod_2['price'])
                cheaper = prod_1 if prod_1['price'] < prod_2['price'] else prod_2
                costlier = prod_2 if prod_1['price'] < prod_2['price'] else prod_1

                st.markdown(f"""
                <div class="verdict-box">
                    <h4 style="margin-top:0; color: #60a5fa;">⚖️ AI Sales Representative Comparison Verdict</h4>
                    <p>• <b>Price Difference:</b> <b>{costlier['name']}</b> is ₹{price_diff:,} more expensive than <b>{cheaper['name']}</b>.</p>
                    <p>• <b>Performance Profile:</b> {prod_1['name']} is powered by <b>{prod_1['processor']}</b> with {prod_1['gpu']}, whereas {prod_2['name']} features <b>{prod_2['processor']}</b> with {prod_2['gpu']}.</p>
                    <p>• <b>Sales Verdict:</b> If your focus is high-value coding and multitasking within budget, <b>{cheaper['name']}</b> (₹{cheaper['price']:,}) is the optimal choice. If your workflows require higher single-core or dedicated processing, consider <b>{costlier['name']}</b>.</p>
                </div>
                """, unsafe_allow_html=True)

                c_action1, c_action2 = st.columns(2)
                with c_action1:
                    if st.button(f"🛒 Book / Reserve {prod_1['name']}", key=f"bk_{prod_1['product_id']}", use_container_width=True):
                        st.session_state.prefill_query = f"Mujhe {prod_1['name']} book karna hai, details batayein."
                        st.info(f"Switched query to chat for {prod_1['name']}. Go to '💬 AI Sales Copilot' tab to continue.")
                with c_action2:
                    if st.button(f"🛒 Book / Reserve {prod_2['name']}", key=f"bk_{prod_2['product_id']}", use_container_width=True):
                        st.session_state.prefill_query = f"Mujhe {prod_2['name']} book karna hai, details batayein."
                        st.info(f"Switched query to chat for {prod_2['name']}. Go to '💬 AI Sales Copilot' tab to continue.")
    else:
        st.warning("Product catalog is empty. Please check if FastAPI backend is connected.")


# ==========================================
# TAB 3: CRM LEADS & RESERVATION DESK
# ==========================================

with tab_leads:
    st.subheader("📝 Customer Callback & Deal Reservation Desk")
    st.caption("Sales representatives can review inbound leads or customers can register direct reservation requests.")

    c_form, c_table = st.columns([1, 1.4], gap="large")

    with c_form:
        st.markdown("##### 📌 New Callback / Deal Request")
        with st.form("reserve_deal_form", clear_on_submit=True):
            name_val = st.text_input("Customer Name*", placeholder="Rahul Sharma")
            phone_val = st.text_input("Mobile Number*", placeholder="9876543210")
            email_val = st.text_input("Email Address (Optional)", placeholder="rahul@example.com")
            
            product_options = ["None / General Inquiry"] + [f"{p['product_id']} - {p['name']} (₹{p['price']:,})" for p in all_products]
            selected_model = st.selectbox("Interested Laptop Model", product_options)
            
            note_val = st.text_area("Requirements / Delivery City", placeholder="Looking for immediate delivery, need advice on RAM upgrade...")
            
            submit_btn = st.form_submit_button("⚡ Submit Callback Request", use_container_width=True)
            if submit_btn:
                if not phone_val:
                    st.error("Please enter a valid mobile number.")
                else:
                    interested_pid = selected_model.split()[0] if selected_model != "None / General Inquiry" else None
                    ok = submit_lead(
                        session_id=st.session_state.session_id,
                        name=name_val,
                        phone=phone_val,
                        email=email_val,
                        notes=note_val,
                        product_id=interested_pid
                    )
                    if ok:
                        st.success("🎉 Callback request submitted! Hamari sales team aapko 30 minutes ke andar call karegi.")
                        st.cache_data.clear()
                    else:
                        st.error("Failed to submit request. Please check if FastAPI server is running.")

    with c_table:
        st.markdown("##### 📋 Live CRM Qualified Leads")
        leads_data = fetch_leads()
        if leads_data:
            ldf = pd.DataFrame(leads_data)
            lead_cols = ["id", "customer_name", "phone", "email", "interested_product_id", "lead_status"]
            avail_cols = [c for c in lead_cols if c in ldf.columns]
            st.dataframe(ldf[avail_cols], use_container_width=True, hide_index=True)
            
            csv = ldf.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Leads as CSV",
                csv,
                "technova_leads.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("No leads captured yet. Leads captured by AI in chat or submitted via form will appear here automatically.")
