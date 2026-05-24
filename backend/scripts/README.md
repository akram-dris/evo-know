# 📜 Database Initialization & Seeding Scripts (`scripts/`)

This directory contains standalone automation scripts designed to establish the relational schemas, vector storage directories, and graph constraints required by the **Cloud-Native Knowledge Management Update System**.

```
scripts/
└── init_databases.py           # Automated PostgreSQL & Neo4j Schema Initializer
```

---

## ⚡ Automated Execution Guide

To initialize both PostgreSQL and Neo4j without needing to install local database drivers or configure a local Python virtual environment, execute the script inside the already-running API Gateway container using the command for your shell:

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

### 🔍 How It Works Under the Hood:
1. **Environment Inheritance:** By running inside the `api-gateway` container, the script automatically inherits the active Docker Compose `.env` configuration (`POSTGRES_HOST=postgres`, `NEO4J_URI=bolt://neo4j:7687`).
2. **`try-except` Isolation:** The script wraps `load_dotenv()` in a try-except block, preventing `AssertionError` crashes when executed via standard input (`stdin`).
3. **PostgreSQL Seeding:** Connects to Postgres and automatically executes the DDL statements to create 10 relational tables (`documents`, `knowledge_chunks`, `obsolescence_scores`, `audit_log`, `access_logs`, etc.) along with optimized foreign key indexes.
4. **Neo4j Seeding:** Connects to the Neo4j graph database and enforces Cypher uniqueness constraints on core entity nodes (`Document`, `Concept`, `Department`, `Employee`).

---

## 🛠️ Verification

Upon successful execution, the terminal will display the following green confirmation messages:

```text
🚀 Starting Database Initialization Script...
🔄 Connecting to PostgreSQL at postgres:5432...
⚡ Executing PostgreSQL schema creation...
✅ PostgreSQL tables and indexes initialized successfully.
🔄 Connecting to Neo4j at bolt://neo4j:7687...
⚡ Executing Neo4j constraints creation...
✅ Neo4j constraints initialized successfully.
🎉 All databases initialized successfully!
```
