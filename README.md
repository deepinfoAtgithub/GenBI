# 🤖 Agentic GenBI Enterprise Platform
### *From Passive Dashboards to Autonomous Decision-Making*

---

## 📖 Overview
This repository contains a functional **Proof-of-Concept (PoC)** for a "To-Be" Agentic AI Architecture. 

Instead of requiring a human to manually monitor a Power BI dashboard, this platform uses an **Autonomous AI Agent** to audit data in **Azure Synapse**, reason over anomalies using LLMs, and provide proactive business recommendations via a **Streamlit** interface.

---

## 🏗️ System Architecture
The platform follows a modern, cost-effective **"ELT + AI"** pattern:



* **Data Warehouse (Storage):** `Azure Synapse Analytics (SQL Pool)` hosting the AdventureWorks SalesLT dataset.
* **Semantic Layer (Governance):** `dbt` (Data Build Tool) standardizes raw tables into business-ready "Marts" (e.g., `fct_sales_performance`).
* **Agentic Brain (Reasoning):** `Python` (LangGraph/LangChain) in Google Colab executes the reasoning loop using `GPT-4o`.
* **UI/UX (Presentation):** `Streamlit` provides an interactive natural language interface for end-users to trigger "AI Audits."

---

## 🌟 Key Features
* **Semantic Guardrails:** By using **dbt**, the AI Agent is prevented from "hallucinating" math. It queries a single source of truth for metrics like Gross Margin and Revenue.
* **Cost-Optimized Inference:** Instead of sending millions of rows to the LLM, the architecture uses **Warehouse Aggregation** to send only "High-Signal" anomalies (e.g., categories where Margin < 15%).
* **Proactive "Watchdog" Logic:** The system doesn't just show a chart; it analyzes the root cause of margin drops (Cost vs. Pricing) and suggests immediate supply chain actions.
* **Production Readiness:** Includes `dbt Tests` for data quality and `Streamlit Caching` for high-performance user experiences.

---

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **Cloud** | Azure (Synapse, SQL Pool) |
| **Transformation** | dbt Cloud / dbt Core |
| **Language** | Python 3.12, SQL |
| **AI Framework** | LangChain, LangGraph, OpenAI (GPT-4o) |
| **Web Framework** | Streamlit |
| **Connectivity** | ODBC Driver 18, pyodbc |

---
## ⚖️ Disclaimer
**Please Read Carefully:**

* **"As-Is" Basis:** This repository is provided for educational and portfolio purposes only. The software is provided "as is," without warranty of any kind, express or implied.
* **Cloud Costs:** Using this project involves third-party services (Azure Synapse, OpenAI GPT-4o). Users are solely responsible for any cloud consumption costs or API charges incurred.
* **Data Security:** This is a Proof-of-Concept. Before using this architecture with sensitive enterprise data, ensure you have implemented proper OAuth, encryption, and network security protocols.
* **GPL 3.0 Compliance:** In accordance with the GNU GPL v3.0, any derivative works or distributions of this code must also be made available under the same license.


## 🚀 Getting Started

### 1. dbt Transformation
Navigate to your dbt project and run the following to build the Semantic Layer:
```bash
dbt run
dbt test

---
