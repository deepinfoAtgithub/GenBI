import streamlit as st
import pandas as pd
import pyodbc
from langchain_openai import ChatOpenAI
from datetime import datetime

# 1. AUTHENTICATION & SECURITY (Must be at the top)
# Note: st.user is the new standard in Streamlit 1.35+
if not st.user.is_logged_in:
    st.set_page_config(page_title="GenBI Analytics Login", layout="centered")
    st.header("🔐 GenBI Enterprise Platform")
    st.info("Access to this Agentic Analytics layer is restricted. Please log in to continue.")
    if st.button("Log in with Google"):
        st.login("google")
    st.stop()

# 2. EMAIL WHITELIST (Replace with your email)
AUTHORIZED_USERS = ["deepak.adlakha@gmail.com"] 

if st.user.email not in AUTHORIZED_USERS:
    st.set_page_config(page_title="Access Denied")
    st.error(f"Access Denied for {st.user.email}. This attempt has been logged.")
    if st.button("Log out"):
        st.logout()
    st.stop()

# 3. MAIN APP CONFIGURATION
st.set_page_config(page_title="GenBI Agentic Platform", layout="wide")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.write(f"👋 Welcome, **{st.user.name}**")
if st.sidebar.button("Logout"):
    st.logout()

st.title("🤖 Agentic GenBI Enterprise Platform")
st.markdown("---")

# 4. SECRETS & DATABASE CONNECTION
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
OPENAI_KEY = st.secrets["OPENAI_API_KEY"]

conn_str = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server=tcp:genbiretailserver.database.windows.net,1433;"
    f"Database=RetailServices;"
    f"Uid={DB_USER};Pwd={DB_PASS};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

@st.cache_data(ttl=3600)
def fetch_data():
    query = "SELECT category_name, SUM(gross_revenue) as Revenue, SUM(gross_profit) as Profit FROM dbt_dadlakha.fct_sales_performance GROUP BY category_name"
    with pyodbc.connect(conn_str) as conn:
        return pd.read_sql(query, conn)

# 5. SIDEBAR CONTROLS
st.sidebar.header("Agent Settings")
margin_threshold = st.sidebar.slider("Margin Alert Threshold (%)", 0, 50, 15)
run_audit = st.sidebar.button("Run Autonomous Audit")

# 6. DASHBOARD RENDERING
try:
    df = fetch_data()
    df['Margin %'] = (df['Profit'] / df['Revenue'].replace(0, 1)) * 100

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Category Performance")
        st.bar_chart(df, x="category_name", y="Margin %")
        st.dataframe(df.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Margin %': '{:.2f}%'}), use_container_width=True)

    with col2:
        st.subheader("🧠 Agent Insights")
        if run_audit:
            # Audit Log for your records (visible in Streamlit logs)
            print(f"[AUDIT] {st.user.email} ran an Autonomous Audit at {datetime.now()}")
            
            with st.spinner("Agent is reasoning over the semantic layer..."):
                anomalies = df[df['Margin %'] < margin_threshold]
                if not anomalies.empty:
                    st.warning(f"🚨 Found {len(anomalies)} anomalies below threshold.")
                    
                    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_KEY)
                    prompt = f"The following retail categories have low margins: {anomalies.to_string()}. As a senior retail consultant, suggest 2 urgent strategic actions."
                    response = llm.invoke(prompt)
                    st.write(response.content)
                else:
                    st.success("✅ All categories are performing within threshold.")
except Exception as e:
    st.error(f"Critical error connecting to the Data Warehouse: {e}")
    