# 🚀 Cloud-Native Knowledge Management (KM) Update System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Cloud%20Native-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge%20Graph-018bff?logo=neo4j)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-Event%20Bus-231F20?logo=apachekafka)

---

## ⚡ 1. Quick Start & Execution Guide (Straight to the Point)

This section provides the exact, copy-paste commands required to launch the complete 13-container microservices ecosystem, initialize the dual databases, and execute live ingestion and querying tests.

### 🛠️ Step 1: Environment Preparation
Clone the repository and configure your environment variables:

```bash
git clone https://github.com/akram-dris/evo-know.git
cd evo-know
cp .env.example .env
```
*(Optional: Open `.env` and add your active `GEMINI_API_KEY` and `SLACK_BOT_TOKEN`).*

### 🐳 Step 2: Build & Launch Cloud-Native Infrastructure
Leverage Docker BuildKit cache mounts to accelerate building all 8 AI microservices, then spin up the entire cluster:

```bash
# 1. Build all services (uses BuildKit cache for sub-minute builds)
docker compose build

# 2. Start all 13 containers in detached mode
docker compose up -d
```

Verify that all containers are healthy and running:
```bash
docker compose ps
```

### 🐘 Step 3: Initialize Hybrid Databases (PostgreSQL & Neo4j)
Execute the automated initialization script directly inside the API Gateway container. Since syntax differs across operating systems and shells, choose the command matching your terminal:

**For Linux / macOS / Windows Git Bash:**
```bash
docker compose exec -T api-gateway python - < scripts/init_databases.py
```

**For Windows PowerShell:**
```powershell
Get-Content .\scripts\init_databases.py -Raw | docker compose exec -T api-gateway python -
```

**For Windows Command Prompt (CMD):**
```cmd
docker compose exec -T api-gateway python - < scripts/init_databases.py
```

*Expected Output:* Confirmation messages indicating successful creation of PostgreSQL tables and Neo4j constraints.

---

## 🎯 3. Live End-to-End Pipeline Validation

Once the cluster is up and databases are initialized, verify the system's core capabilities using `curl` from your terminal. Choose the command matching your operating system and shell:

### 🟢 Test 1: API Gateway Health Check
Verify that the Gateway is operational and communicating with the databases:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -s http://127.0.0.1:8000/health
```

**For Windows PowerShell:**
```powershell
curl.exe -s http://127.0.0.1:8000/health
# Or: Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

**For Windows Command Prompt (CMD):**
```cmd
curl -s http://127.0.0.1:8000/health
```

*Expected Output:* `{"status":"online","service":"api-gateway","database":"healthy"}`

### 🟢 Test 2: Knowledge Ingestion & Vector Indexing
Upload a sample knowledge document (`sample_knowledge.txt`). The system will automatically chunk, embed, store in Postgres, index in FAISS, create Neo4j graph nodes, and publish a Kafka event:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -s -X POST "http://127.0.0.1:8000/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_knowledge.txt" \
  -F "department=AI Research" \
  -F "uploaded_by=Akram Dris"
```

**For Windows PowerShell:**
```powershell
curl.exe -s -X POST "http://127.0.0.1:8000/ingest" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@sample_knowledge.txt" `
  -F "department=AI Research" `
  -F "uploaded_by=Akram Dris"
```

**For Windows Command Prompt (CMD):**
```cmd
curl -s -X POST "http://127.0.0.1:8000/ingest" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@sample_knowledge.txt" ^
  -F "department=AI Research" ^
  -F "uploaded_by=Akram Dris"
```

*Expected Output:* `{"status":"success","document_id":"...","chunks_created":5,"message":"Document successfully ingested..."}`

### 🟢 Test 3: Semantic Search & Retrieval
Query the ingested knowledge base in natural language:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -s -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the role of Apache Kafka in the system?", "top_k": 1}'
```

**For Windows PowerShell:**
```powershell
curl.exe -s -X POST "http://127.0.0.1:8000/query" `
  -H "Content-Type: application/json" `
  -d '{"question": "What is the role of Apache Kafka in the system?", "top_k": 1}'
```

**For Windows Command Prompt (CMD):**
```cmd
curl -s -X POST "http://127.0.0.1:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What is the role of Apache Kafka in the system?\", \"top_k\": 1}"
```

*Expected Output:* Returns the exact matching chunk explaining Kafka orchestration with an 89.3% similarity score.

---

## 🏗️ 4. Cloud-Native Architecture & Monorepo Structure

```
evo-know/
├── docker-compose.yml              # Orchestrates 13 containers & network
├── .env                            # Environment variables & secrets
├── README.md                       # Main Quick Start & Execution Guide
│
├── services/                       # 8 AI & Core Microservices (See services/README.md)
├── shared/                         # Shared Python Libraries (See shared/README.md)
├── scripts/                        # Database Seeding Scripts (See scripts/README.md)
├── docs/                           # Documentation & Reports (See docs/README.md)
└── monitoring/                     # Prometheus Metrics Setup (See monitoring/README.md)
```

### 📬 Microservices Ecosystem Summary
- **`api-gateway` (Port 8000):** FastAPI REST entry point.
- **`t1-prediction`:** AI obsolescence & knowledge decay forecasting.
- **`t2-report-generation`:** Gemini LLM automated markdown report synthesis.
- **`t3-knowledge-fusion`:** NLP deduplication & intelligent chunk merging.
- **`t4-consistency-check`:** NLI DeBERTa contradiction & anomaly detection.
- **`t5-knowledge-discovery`:** Association rule mining (Apriori/FP-Growth).
- **`orchestrator`:** Automated background daemon & scheduler.
- **`slack-bot` (Port 3000):** Enterprise conversational interface.

---
**Open-Source Cloud-Native Knowledge Management Platform.**
