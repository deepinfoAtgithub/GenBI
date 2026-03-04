import streamlit as st
import pandas as pd
import pyodbc
import os
from langchain_openai import ChatOpenAI

# 1. Page Config
st.set_page_config(page_title="GenBI Agentic Platform", layout="wide")
st.title("🤖 Agentic GenBI Enterprise Platform")
st.markdown("---")

# 2. Access secrets from Streamlit's native Cloud Secrets
# (We will set these in the Streamlit Dashboard later)
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
OPENAI_KEY = st.secrets["OPENAI_API_KEY"]

# 3. Connection String
conn_str = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server=tcp:genbiretailserver.database.windows.net,1433;"
    f"Database=RetailServices;"
    f"Uid={DB_USER};Pwd={DB_PASS};"
    "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)

@st.cache_data(ttl=3600)
def fetch_data():
    query = "SELECT category_name, SUM(gross_revenue) as Revenue, SUM(gross_profit) as Profit FROM dbt_dadlakha.fct_sales_performance GROUP BY category_name"
    with pyodbc.connect(conn_str) as conn:
        return pd.read_sql(query, conn)

# 4. Sidebar - Control Room
st.sidebar.header("Agent Settings")
margin_threshold = st.sidebar.slider("Margin Alert Threshold (%)", 0, 50, 15)
run_audit = st.sidebar.button("Run Autonomous Audit")

# 5. Main Dashboard Logic
try:
    df = fetch_data()
    df['Margin %'] = (df['Profit'] / df['Revenue'].replace(0, 1)) * 100

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Category Performance")
        st.bar_chart(df, x="category_name", y="Margin %")
        st.dataframe(df.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Margin %': '{:.2f}%'}))

    with col2:
        st.subheader("Agent Insights")
        if run_audit:
            with st.spinner("Agent is reasoning..."):
                anomalies = df[df['Margin %'] < margin_threshold]
                if not anomalies.empty:
                    st.warning(f"Found {len(anomalies)} categories below threshold!")
                    
                    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_KEY)
                    
                    prompt = f"The following categories have low margins: {anomalies.to_string()}. Suggest 2 urgent actions."
                    response = llm.invoke(prompt)
                    st.write(response.content)
                else:
                    st.success("All categories are performing within threshold.")
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    