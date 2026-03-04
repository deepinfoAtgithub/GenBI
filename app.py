import streamlit as st
import pandas as pd
import pyodbc
from langchain_openai import ChatOpenAI

# 1. AUTHENTICATION (STABLE VERSION)
if not st.user.is_logged_in:
    st.set_page_config(page_title="GenBI Login", layout="centered")
    st.header("🔐 GenBI Enterprise Platform")
    st.info("Authorized personnel only. Please authenticate via Google.")
    # We call st.login without "google" if you only have one [auth] provider in secrets
    if st.button("Log in with Google"):
        st.login() 
    st.stop()

# 2. EMAIL WHITELIST
AUTHORIZED_USERS = ["deepak.adlakha@gmail.com"]

if st.user.email not in AUTHORIZED_USERS:
    st.error(f"Access Denied for {st.user.email}.")
    if st.button("Log out"):
        st.logout()
    st.stop()

# 3. MAIN DASHBOARD CONFIG
st.set_page_config(page_title="GenBI Agentic Platform", layout="wide")
st.sidebar.write(f"Logged in: **{st.user.name}**")
if st.sidebar.button("Logout"):
    st.logout()

st.title("🤖 Agentic GenBI Enterprise Platform")
st.markdown("---")

# 4. DATABASE & SECRETS
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

# 5. UI LOGIC
try:
    df = fetch_data()
    df['Margin %'] = (df['Profit'] / df['Revenue'].replace(0, 1)) * 100

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📊 Category Performance")
        st.bar_chart(df, x="category_name", y="Margin %")
        st.dataframe(df.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Margin %': '{:.2f}%'}))

    with col2:
        st.subheader("🧠 Agent Insights")
        margin_threshold = st.slider("Margin Alert Threshold (%)", 0, 50, 15)
        if st.button("Run Autonomous Audit"):
            with st.spinner("AI is reasoning..."):
                anomalies = df[df['Margin %'] < margin_threshold]
                if not anomalies.empty:
                    st.warning(f"Found {len(anomalies)} categories below threshold!")
                    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_KEY)
                    response = llm.invoke(f"Retail categories with low margins: {anomalies.to_string()}. Suggest 2 actions.")
                    st.write(response.content)
                else:
                    st.success("All categories healthy.")
except Exception as e:
    st.error(f"Error: {e}")