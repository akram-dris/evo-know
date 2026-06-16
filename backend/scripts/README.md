# 📜 Database Initialization Scripts (`scripts/`)

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
docker compose exec api-gateway python backend/scripts/init_databases.py
```

**For Windows PowerShell:**
```powershell
docker compose exec api-gateway python backend/scripts/init_databases.py
```

**For Windows Command Prompt (CMD):**
```cmd
docker compose exec api-gateway python backend/scripts/init_databases.py
```

### 🔍 What the script does:
1. **Environment Inheritance:** By running inside the `api-gateway` container, the script automatically inherits the active Docker Compose `.env` configuration (`POSTGRES_HOST=postgres`, `NEO4J_URI=bolt://neo4j:7687`).
2. **PostgreSQL Schema:** Creates 10 relational tables (`documents`, `knowledge_chunks`, `obsolescence_scores`, `audit_log`, `access_logs`, etc.) along with optimized foreign key indexes.
3. **Default Users:** Seeds 3 user accounts (Admin, Expert, Reader). No demonstration documents are seeded — documents are uploaded directly through the web interface.
4. **Neo4j Constraints:** Enforces Cypher uniqueness constraints on core entity nodes (`Document`, `Concept`, `Department`, `Employee`).

---

## 🛠️ Verification

Upon successful execution, the terminal will display the following confirmation messages:

```text
🚀 Starting Database Initialization Script...
🔄 Connecting to PostgreSQL at postgres:5432...
⚡ Executing PostgreSQL schema creation...
🌱 Seeding default users (Admin, Expert, Reader)...
✅ PostgreSQL tables, indexes, and default users initialized successfully.
🔄 Connecting to Neo4j at bolt://neo4j:7687...
⚡ Executing Neo4j constraints creation...
✅ Neo4j constraints initialized successfully.
🎉 All databases initialized successfully!
```
