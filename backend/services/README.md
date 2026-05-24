# 🏢 Microservices Ecosystem (`services/`)

This directory houses the seven decoupled, event-driven microservices that power the **Cloud-Native Knowledge Management Update System**. Each service is fully containerized using optimized Python `slim` base images and communicates asynchronously via Apache Kafka.

```
services/
├── api-gateway/                # FastAPI REST API — Centralized Entry Point
├── t1-prediction/              # AI Task 1: Knowledge Decay & Obsolescence Forecasting
├── t2-report-generation/       # AI Task 2: Gemini LLM Automated Summary Reports
├── t3-knowledge-fusion/        # AI Task 3: Intelligent NLP Chunk Deduplication & Merging
├── t4-consistency-check/       # AI Task 4: NLI DeBERTa Contradiction & Anomaly Detection
├── t5-knowledge-discovery/     # AI Task 5: Association Rule Mining (Apriori/FP-Growth)
└── orchestrator/               # AI Daemon: Background Task Scheduler & Conflict Auditing
```

---

## 🚀 Microservice Architecture & Event Flow

1. **Ingestion (`api-gateway`):** Receives HTTP uploads, chunks text, stores vectors in FAISS/Postgres, creates Neo4j nodes, and publishes `document.ingested` to Kafka.
2. **Asynchronous AI Processing (`t1` - `t5`):** Independent consumer daemons listen to Kafka topics (`document.ingested`, `consistency.checked`, etc.) and perform heavy machine learning tasks in the background without blocking the Gateway.
3. **Orchestration (`orchestrator`):** Manages periodic batch jobs, maintains system consistency, and triggers audit workflows.

---

## 🛠️ Individual Service Execution & Logs

To inspect the real-time background activity or logs of any specific microservice within the Docker Compose cluster, run:

```bash
# View real-time logs for the API Gateway
docker compose logs -f api-gateway

# View AI background worker logs
docker compose logs -f t1-prediction t3-knowledge-fusion t4-consistency-check
```

To restart a specific microservice after making local code changes:
```bash
docker compose up -d --build t2-report-generation
```
