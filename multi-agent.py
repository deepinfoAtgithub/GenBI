import streamlit as st
import pandas as pd
import pyodbc
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# --- 1. LOCAL AUTHENTICATION MOCK (For Colab Testing) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.set_page_config(page_title="GenBI Login", layout="centered")
    st.header("GenBI Enterprise Platform")
    st.info("Authorized personnel only. Please authenticate via Google.")
    if st.button("Log in with Google (Local Colab Mode)"):
        st.session_state.logged_in = True
        st.rerun()
    st.stop() # Halts execution until logged in

# --- 2. PAGE CONFIG (Authenticated) ---
st.set_page_config(page_title="GenBI Multi-Agent Platform", layout="wide")

# Sidebar Profile & Logout
st.sidebar.write("Logged in: **Deepak Adlakha** *(Local Admin)*")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🤖 Agentic GenBI: Multi-Agent Command Center")
st.markdown("---")

# --- 3. SECRETS & DATABASE CONNECTION ---
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_KEY, temperature=0.1)

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=tcp:genbiretailserver.database.windows.net,1433;"
    "Database=RetailServices;"
    f"Uid={DB_USER};Pwd={DB_PASS};"
    "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)

# --- 4. DATA FETCHING (For the UI) ---
@st.cache_data(ttl=10) # Set a low Time-To-Live so it updates frequently
def fetch_vision_alerts():
    query = """
        SELECT TOP 3 audit_timestamp, image_name, executive_memo 
        FROM visual_audit_logs 
        ORDER BY audit_timestamp DESC
    """
    try:
        with pyodbc.connect(conn_str) as conn:
            return pd.read_sql(query, conn)
    except Exception:
        # Returns an empty dataframe if the table doesn't exist yet
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_sales_data():
    query = """
        SELECT category_name, SUM(gross_revenue) as Revenue, SUM(gross_profit) as Profit
        FROM dbt_dadlakha.fct_sales_performance
        GROUP BY category_name
    """
    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql(query, conn)
        df['Margin %'] = (df['Profit'] / df['Revenue'].replace(0, 1)) * 100
        return df

# --- 5. LANGGRAPH: AGENT DEFINITIONS ---
class AgenticState(TypedDict):
    target_category: str
    finance_alert: str
    logistics_context: str
    final_recommendation: str

def finance_auditor(state: AgenticState):
    # Dynamically read the category selected by the user in the UI
    category = state['target_category']

    return {
        "target_category": category,
        "finance_alert": f"Urgent Audit Required: The margin for '{category}' needs investigation. Please cross-reference with supply chain data to identify potential root causes like COGS spikes, high freight, or vendor delays."
    }

def logistics_specialist(state: AgenticState):
    category = state['target_category']
    query = f"""
        SELECT vendor_name, inventory_status, avg_lead_time_days, total_freight_cost
        FROM dbt_dadlakha.fct_logistics_health
        WHERE category_name = '{category}' AND (inventory_status = 'CRITICAL' OR avg_lead_time_days > 14)
    """
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn)
        context = df.to_string(index=False) if not df.empty else "No logistics anomalies found."
    except Exception as e:
        context = f"Database Error: {str(e)}"
    return {"logistics_context": context}

def executive_synthesizer(state: AgenticState):
    prompt = PromptTemplate.from_template(
        """You are the Lead GenBI AI. Review the findings from your specialized agents:
        Finance Report: {finance_alert}
        Logistics Data: {logistics_context}

        Draft a concise, 3-bullet-point executive summary connecting the financial drop
        to the supply chain data, and recommend an immediate business action."""
    )
    chain = prompt | llm
    response = chain.invoke({"finance_alert": state["finance_alert"], "logistics_context": state["logistics_context"]})
    return {"final_recommendation": response.content}

# Compile Graph
workflow = StateGraph(AgenticState)
workflow.add_node("Finance", finance_auditor)
workflow.add_node("Logistics", logistics_specialist)
workflow.add_node("Executive", executive_synthesizer)
workflow.set_entry_point("Finance")
workflow.add_edge("Finance", "Logistics")
workflow.add_edge("Logistics", "Executive")
workflow.add_edge("Executive", END)
multi_agent_app = workflow.compile()


# --- 6. UI DASHBOARD RENDERING ---

# Helper function to run the agent graph and update the UI
def run_agentic_audit(target_category, mode_name):
    with st.status(f"Initializing {mode_name} for '{target_category}'...", expanded=True) as status:
        st.write("🕵️‍♂️ **Agent A (Finance):** Scanning margins and formulating alert...")
        st.write(f"📦 **Agent B (Logistics):** Querying vendor & freight data for {target_category}...")
        st.write("🧠 **Executive LLM:** Synthesizing root-cause analysis...")

        initial_state = {
            "target_category": target_category,
            "finance_alert": "",
            "logistics_context": "",
            "final_recommendation": ""
        }

        result = multi_agent_app.invoke(initial_state)
        status.update(label="Audit Complete!", state="complete", expanded=False)

    st.success("### Executive Action Memo")
    st.markdown(result["final_recommendation"])

# Render the Dashboard
try:

  # --- NEW: Live Vision Alerts Feed ---
    df_alerts = fetch_vision_alerts()

    if not df_alerts.empty:
        st.error("🚨 **LIVE WAREHOUSE ALERTS (Agent C - Vision)**")
        for index, row in df_alerts.iterrows():
            with st.expander(f"📷 Alert generated at {row['audit_timestamp']} for {row['image_name']}"):
                st.markdown(row['executive_memo'])
        st.markdown("---")

    df_sales = fetch_sales_data()

    col1, col2 = st.columns([1.5, 1])

    # Left Column: Standard BI
    with col1:
        st.subheader("📊 Global Financial View")
        st.bar_chart(df_sales, x="category_name", y="Margin %")
        st.dataframe(df_sales.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Margin %': '{:.2f}%'}))

    # Right Column: Multi-Agent Controls
    with col2:
        st.subheader("🧠 Multi-Agent Orchestration")
        st.info("Deploys parallel AI agents to audit Finance and Supply Chain data.")

        # MODE 1: The Autonomous Watchdog (Great for Demos)
        st.write("#### 🚨 Autonomous Mode")
        st.caption("Agent automatically scans all categories to detect margin anomalies.")
        if st.button("Auto-Detect Anomalies", type="primary", use_container_width=True):
            # In a full production build, Agent A would find 'Bikes' dynamically from the dataframe.
            # For this scenario, we trigger the known anomaly.
            run_agentic_audit("Bikes", "Autonomous Watchdog")

        st.divider()

        # MODE 2: Manual Deep Dive
        st.write("#### 🔍 Manual Override")
        st.caption("Force the agents to audit a specific product category.")
        categories = df_sales['category_name'].unique().tolist()
        selected_category = st.selectbox("Select Category:", categories, label_visibility="collapsed")

        if st.button("Audit Selected Category", use_container_width=True):
            run_agentic_audit(selected_category, "Manual Audit")

except Exception as e:
    st.error(f"System Offline. Error: {e}")
