# ⚙️ EvoKnow Backend Services

This is the backend core of the **Cloud-Native Knowledge Management (KM) Update System**. It consists of 7 Python microservices running on FastAPI and communicating asynchronously via Apache Kafka.

---

## 🏗️ Folder Structure
```
backend/
├── services/
│   ├── api-gateway/            # FastAPI REST entry gateway (Port 8000)
│   ├── t1-prediction/          # Obsolescence Forecasting (LSTM / Prophet)
│   ├── t2-report-generation/   # LLM Summary Report Synthesis (Gemini API)
│   ├── t3-knowledge-fusion/    # Semantic clustering & duplicate consolidation (DBSCAN)
│   ├── t4-consistency-check/   # Logic checking & NLI contradiction validation (Neo4j)
│   ├── t5-knowledge-discovery/ # NER extraction & Association rules mining (Apriori)
│   └── orchestrator/           # Daily lifecycle beat scheduler & conflict resolver
├── shared/                     # Shared database drivers, embeddings, and Kafka code
├── scripts/                    # Seeding and database schema init scripts
├── data/                       # Ingestion directory (raw/processed files)
├── monitoring/                 # Prometheus setup metrics configs
└── requirements-base.txt       # Unified Python library requirements
```

---

## 🛠️ Setup & Quick Execution

### 1. Initialize databases:
Execute the database creation and Neo4j constraint seeding scripts inside the gateway service:
```bash
docker compose exec -T api-gateway python - < backend/scripts/init_databases.py
```

### 2. Batch ingestion:
To batch ingest existing PDF/DOCX templates from `./backend/data/raw/` into FAISS vector database and Neo4j, run:
```bash
docker compose exec -T api-gateway python - < backend/scripts/seed_data.py
```

### 3. API Reference:
Interactive OpenAPI specifications (Swagger UI) are hosted at:
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
