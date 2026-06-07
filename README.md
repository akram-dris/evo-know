# 🚀 Cloud-Native Knowledge Management (KM) Update System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Cloud%20Native-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge%20Graph-018bff?logo=neo4j)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-Event%20Bus-231F20?logo=apachekafka)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-white?logo=ollama)

---

## ⚡ 1. Quick Start & Execution Guide (Straight to the Point)

This section provides the exact, copy-paste commands required to launch the complete 14-container microservices ecosystem (now featuring 100% local AI via Ollama), initialize the dual databases, and execute live ingestion and querying tests.

### 🛠️ Step 1: Environment Preparation
Clone the repository and configure your environment variables. No external API keys are required for core functionality!

```bash
git clone https://github.com/akram-dris/evo-know.git
cd evo-know
cp .env.example .env
```
*(The default `.env` is pre-configured to use the local Ollama service for all LLM operations).*

### 🐳 Step 2: Build & Launch Cloud-Native Infrastructure
Leverage Docker BuildKit cache mounts to accelerate building all AI microservices, then spin up the entire cluster:

```bash
# 1. Build all services (uses BuildKit cache for sub-minute builds)
docker compose build

# 2. Start all 14 containers in detached mode
docker compose up -d
```

Verify that all containers are healthy and running:
```bash
docker compose ps
```

### 🧠 Step 2.5: Initialize Local AI Model (Critical Step)
EvoKnow now runs 100% locally using Ollama. Before using AI features (like RAG or Report Generation), you **must** download the language model into the running Ollama container:

```bash
docker exec -it evo-know-ollama-1 ollama run llama3
```
*(Wait for the download to complete and the "Send a message" prompt to appear, then type `/bye` to exit).*

### 🐘 Step 3: Initialize Hybrid Databases (PostgreSQL & Neo4j)
Execute the automated initialization script directly inside the API Gateway container. Since syntax differs across operating systems and shells, choose the command matching your terminal:

**For Linux / macOS / Windows Git Bash:**
```bash
docker exec -i evo-know-api-gateway-1 python - < backend/scripts/init_databases.py
```

**For Windows PowerShell:**
```powershell
Get-Content .\backend\scripts\init_databases.py -Raw | docker exec -i evo-know-api-gateway-1 python -
```

**For Windows Command Prompt (CMD):**
```cmd
docker exec -i evo-know-api-gateway-1 python - < backend/scripts/init_databases.py
```

*Expected Output:* Confirmation messages indicating successful creation of PostgreSQL tables and Neo4j constraints.

---

## 🎯 3. Live End-to-End Pipeline Validation

Once the cluster is up and databases are initialized, verify the system's core capabilities using `curl` from your terminal. Choose the command matching your operating system and shell:

### 🟢 Test 1: API Gateway Health Check
Verify that the Gateway is operational and communicating with the databases:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -i http://127.0.0.1:8000/health
```

**For Windows PowerShell:**
```powershell
curl.exe -i http://127.0.0.1:8000/health
```

**For Windows Command Prompt (CMD):**
```cmd
curl -i http://127.0.0.1:8000/health
```

*Expected Output:* `{"status":"online","service":"api-gateway","database":"healthy"}`

### 🟢 Test 2: Knowledge Ingestion & Vector Indexing
Upload a sample knowledge document (`backend/sample_knowledge.txt`). The system will automatically chunk, embed, store in Postgres, index in FAISS, create Neo4j graph nodes, and publish a Kafka event:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/sample_knowledge.txt" \
  -F "department=AI Research" \
  -F "uploaded_by=Akram Dris"
```

**For Windows PowerShell:**
```powershell
curl.exe -X POST "http://127.0.0.1:8000/ingest" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@backend/sample_knowledge.txt" `
  -F "department=AI Research" `
  -F "uploaded_by=Akram Dris"
```

**For Windows Command Prompt (CMD):**
```cmd
curl -X POST "http://127.0.0.1:8000/ingest" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@backend/sample_knowledge.txt" ^
  -F "department=AI Research" ^
  -F "uploaded_by=Akram Dris"
```

*Expected Output:* `{"status":"success","document_id":"...","chunks_created":5,"message":"Document successfully ingested..."}`

### 🟢 Test 3: Semantic Search & Retrieval (RAG via Ollama)
Query the ingested knowledge base in natural language. Ensure you completed Step 2.5 first!

**For Linux / macOS / Windows Git Bash:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What databases are used in the system?", "top_k": 2}'
```

**For Windows PowerShell:**
```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/query" `
  -H "Content-Type: application/json" `
  -d '{"question": "What databases are used in the system?", "top_k": 2}'
```

**For Windows Command Prompt (CMD):**
```cmd
curl -X POST "http://127.0.0.1:8000/api/v1/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What databases are used in the system?\", \"top_k\": 2}"
```

*Expected Output:* An AI-generated answer using the local `llama3` model, citing the source document.

---

## 🏗️ 4. Cloud-Native Architecture & Monorepo Structure

```
evo-know/
├── docker-compose.yml              # Orchestrates 14 containers & network
├── .env                            # Environment variables & configuration
├── README.md                       # Main Quick Start & Execution Guide
│
├── docs/                           # Documentation & Reports (See docs/README.md)
├── frontend/                       # Vue.js 3 + Tailwind CSS Application
└── backend/                        # Backend Services & Shared Libraries
    ├── services/                   # 7 AI & Core Microservices
    ├── shared/                     # Shared Python Libraries
    ├── scripts/                    # Database Seeding Scripts
    └── monitoring/                 # Prometheus Metrics Setup
```

### 📬 Microservices Ecosystem Summary
- **`frontend` (Port 5173):** Vue.js 3 + Tailwind CSS Web Application.
- **`api-gateway` (Port 8000):** FastAPI REST entry point & RAG orchestrator.
- **`ollama` (Port 11434):** Local LLM server running `llama3`.
- **`t1-prediction`:** AI obsolescence & knowledge decay forecasting.
- **`t2-report-generation`:** Local LLM (`llama3`) automated markdown report synthesis.
- **`t3-knowledge-fusion`:** NLP deduplication & intelligent chunk merging.
- **`t4-consistency-check`:** NLI DeBERTa contradiction & anomaly detection.
- **`t5-knowledge-discovery`:** Association rule mining (Apriori/FP-Growth).
- **`orchestrator`:** Automated background daemon & scheduler.

---
**Open-Source Cloud-Native Knowledge Management Platform.**
