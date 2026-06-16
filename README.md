# 🚀 Cloud-Native Knowledge Management (KM) Update System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Cloud%20Native-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge%20Graph-018bff?logo=neo4j)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-Event%20Bus-231F20?logo=apachekafka)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-white?logo=ollama)

---

## ⚡ 1. Step-by-Step Installation & Execution Guide

This guide details the complete step-by-step commands to clone, run, and test the 14-container microservices ecosystem on **Linux**, **macOS**, and **Windows**.

> [!NOTE]
> The database initializes **empty of documents** so that you can upload your files directly using the platform's user interface. Only the three core user accounts (Admin, Expert, Reader) are seeded.

---

### 📂 Step 1: Clone Repository & Create `.env`

#### 🐧 On Linux / macOS / Git Bash:
```bash
# 1. Clone the repository
git clone https://github.com/akram-dris/evo-know.git
cd evo-know

# 2. Copy the environment variables template
cp .env.example .env
```

#### 🪟 On Windows Command Prompt (CMD):
```cmd
:: 1. Clone the repository
git clone https://github.com/akram-dris/evo-know.git
cd evo-know

:: 2. Copy the environment variables template
copy .env.example .env
```

#### 🪟 On Windows PowerShell:
```powershell
# 1. Clone the repository
git clone https://github.com/akram-dris/evo-know.git
cd evo-know

# 2. Copy the environment variables template
Copy-Item .env.example .env
```

---

### 🐳 Step 2: Build & Launch the Microservices Cluster

Run the following commands in your terminal (same for all platforms):

```bash
# 1. Build the microservices containers (uses BuildKit for speed)
docker compose build

# 2. Start all services in the background (detached mode)
docker compose up -d
```

Verify that all containers are running and healthy:
```bash
docker compose ps
```

---

### 🧠 Step 3: Initialize the Local AI Model (Ollama)

EvoKnow runs 100% locally. You must pull the language model inside the Ollama container before utilizing any AI/RAG features:

```bash
docker exec -it evo-know-ollama-1 ollama run llama3
```
*(Wait for the download to complete. Once the model prompt is active, type `/bye` and press Enter to exit back to your terminal).*

---

### 🐘 Step 4: Initialize PostgreSQL & Neo4j Databases

Initialize the database schemas, indexes, and Neo4j graph constraints by executing the initialization script inside the running API Gateway container:

#### 🐧 On Linux / macOS / Git Bash:
```bash
docker compose exec api-gateway python backend/scripts/init_databases.py
```

#### 🪟 On Windows Command Prompt (CMD):
```cmd
docker compose exec api-gateway python backend/scripts/init_databases.py
```

#### 🪟 On Windows PowerShell:
```powershell
docker compose exec api-gateway python backend/scripts/init_databases.py
```

---

### 🌐 Step 5: Access the Web Application & Log In

Once all containers are running and databases are initialized, open your browser and navigate to the application:

*   **Development Server URL:** **`http://localhost:5173`** (Vue.js Vite dev server)
*   **Production Gateway URL:** **`http://localhost`** (Runs on port `80` served by Nginx)

#### 👤 Default Seeded Accounts:
Use these credentials on the login screen to access the application:

| Username | Password | Role | Core Permissions & Capabilities |
| :--- | :--- | :--- | :--- |
| `admin` | `admin_pass_2026` | **Admin** | Full access to dashboards, XAI logs, settings, and account approval management. |
| `expert` | `expert_pass_2026` | **Expert** | Access to all prediction dashboards, semantic fusion, and document upload/delete tools. |
| `reader` | `reader_pass_2026` | **Reader** | Read-only access restricted exclusively to the full-width ChatGPT-style chat assistant. |

---

### 📤 Step 6: Ingest Your First Document

1. Log in using `admin` or `expert` credentials.
2. Navigate to **Base de connaissances** on the sidebar.
3. Click the **Catalogue de Documents** button in the header.
4. Click **+ Importer** in the top-right of the modal.
5. Choose your document (`.txt`, `.pdf`, or `.docx`) and click **Importer**.
6. The document is parsed, chunked, embedded, and added to the search index instantly!

---

## 🎯 2. Live REST API Validation Tests

You can also test and interact with the backend API gateway directly using `curl` from your terminal:

### 🟢 Test 1: API Gateway Health Check
Verify the Gateway is operational and communicating with the databases:

```bash
curl -i http://127.0.0.1:8000/health
```
*Expected Response:* `{"status":"online","service":"api-gateway","database":"healthy"}`

### 🟢 Test 2: Ingest a Document via REST
```bash
# Run this from the root of the project to ingest the sample text file
curl -X POST "http://127.0.0.1:8000/api/v1/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/sample_knowledge.txt" \
  -F "department=Support IT" \
  -F "uploaded_by=admin"
```
*Expected Response:* `{"status":"success","document_id":"...","chunks_created":5,"message":"Document successfully ingested..."}`

### 🟢 Test 3: Semantic Search & RAG Chat Query
Query the ingested knowledge base in natural language (make sure you completed Step 3 first):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What databases are used in the system?", "top_k": 2}'
```
*Expected Response:* An AI-generated answer using the local `llama3` model, referencing the source document.

---

## 🏗️ 3. Cloud-Native Monorepo Structure

```
evo-know/
├── docker-compose.yml              # Orchestrates 14 containers & network
├── .env                            # Environment variables & configuration
├── README.md                       # Main Quick Start & Execution Guide
├── docs/                           # Documentation & Reports
├── frontend/                       # Vue.js 3 + PrimeVue Web Application
└── backend/                        # Backend Services & Shared Libraries
    ├── services/                   # 7 AI & Core Microservices
    ├── shared/                     # Shared Python Libraries
    ├── scripts/                    # Database Initializer & Migration Scripts
    └── monitoring/                 # Prometheus & Metrics Setup
```

---
**Open-Source Cloud-Native Knowledge Management Platform.**
