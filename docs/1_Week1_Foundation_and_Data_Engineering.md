# 1. Week 1 — Foundation, Architecture & Data Engineering

> **Goal**: Stand up the entire Cloud Native infrastructure locally, design and populate the databases, and build the data ingestion pipeline that all 5 task microservices will consume.

---

## Day 1 (Mon): Project Initialization & Repository Structure

### 1.1 Git Repository Setup
```bash
mkdir km-update-system && cd km-update-system
git init
```

### 1.2 Monorepo Structure
The microservices architecture maps directly to the 5 selected tasks from Section 1.4.2 of the thesis, plus shared services:

```
km-update-system/
├── docker-compose.yml              # Orchestrates all services locally
├── .env.example                    # Template for environment variables
├── requirements-base.txt           # Shared Python dependencies
├── README.md
│
├── services/
│   ├── api-gateway/                # FastAPI — Single entry point (API Gateway)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # FastAPI app, mounts sub-routers
│   │   │   ├── routes/
│   │   │   │   ├── ingest.py       # POST /ingest — receives new documents
│   │   │   │   ├── query.py        # POST /query — RAG query endpoint
│   │   │   │   └── health.py       # GET /health — healthcheck
│   │   │   └── config.py           # Pydantic Settings
│   │   └── tests/
│   │
│   ├── t1-prediction/              # Task 1: Prediction of Update Needs
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # Kafka consumer + prediction logic
│   │   │   ├── models/
│   │   │   │   ├── lstm_model.py   # LSTM-based forecasting
│   │   │   │   └── prophet_model.py# Prophet-based forecasting
│   │   │   ├── scoring.py          # Obsolescence Risk Score calculation
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── t2-report-generation/       # Task 2: Auto Report Generation
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # Kafka consumer + LLM report generation
│   │   │   ├── generators/
│   │   │   │   ├── nlg_report.py   # LLM-based NLG report builder
│   │   │   │   └── dashboard.py    # Structured data for dashboards
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── t3-knowledge-fusion/        # Task 3: Intelligent Knowledge Fusion
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # Kafka consumer + fusion logic
│   │   │   ├── clustering/
│   │   │   │   ├── semantic_cluster.py  # K-Means / DBSCAN on embeddings
│   │   │   │   └── deduplication.py     # NLP-based duplicate detection
│   │   │   ├── merger.py           # LLM-assisted merging of duplicates
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── t4-consistency-check/       # Task 4: Automatic Consistency Analysis
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # Kafka consumer + consistency logic
│   │   │   ├── analyzers/
│   │   │   │   ├── nli_checker.py  # NLI-based contradiction detection
│   │   │   │   └── kg_validator.py # Knowledge Graph cross-referencing
│   │   │   ├── report.py           # Consistency report builder
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── t5-knowledge-discovery/     # Task 5: Automatic Knowledge Discovery
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # Kafka consumer + discovery logic
│   │   │   ├── mining/
│   │   │   │   ├── ner_extractor.py     # Named Entity Recognition
│   │   │   │   ├── relation_miner.py    # Association Rule Mining (Apriori/FP-Growth)
│   │   │   │   └── gnn_discovery.py     # GNN for link prediction (if feasible)
│   │   │   └── config.py
│   │   └── tests/
│   │
│   ├── slack-bot/                  # Slack Chatbot Interface
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # slack_bolt app + FastAPI server
│   │   │   ├── handlers/
│   │   │   │   ├── commands.py     # Slash commands (/km-search, /km-status)
│   │   │   │   ├── events.py       # app_mention, message events
│   │   │   │   └── actions.py      # Block Kit button actions
│   │   │   ├── rag/
│   │   │   │   └── pipeline.py     # RAG: embed query → retrieve → LLM answer
│   │   │   └── config.py
│   │   └── tests/
│   │
│   └── orchestrator/               # 5th Sub-Process: AI Orchestration
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py             # Scheduler + orchestration loop
│       │   ├── scheduler.py        # APScheduler / Celery Beat
│       │   ├── conflict_resolver.py# AI-based conflict resolution
│       │   ├── audit_log.py        # XAI traceability logging
│       │   └── config.py
│       └── tests/
│
├── shared/                         # Shared Python package
│   ├── __init__.py
│   ├── database/
│   │   ├── postgres.py             # SQLAlchemy models & session
│   │   ├── neo4j_client.py         # Neo4j driver wrapper
│   │   └── vector_store.py         # FAISS / Qdrant client
│   ├── embeddings/
│   │   └── encoder.py              # Sentence-Transformer embedding wrapper
│   ├── kafka/
│   │   ├── producer.py             # Kafka message producer
│   │   └── consumer.py             # Kafka message consumer base class
│   └── models/
│       └── schemas.py              # Pydantic schemas (KnowledgeChunk, Document, etc.)
│
├── data/
│   ├── raw/                        # Raw enterprise documents (PDF, DOCX, TXT)
│   └── processed/                  # Chunked & embedded data
│
└── scripts/
    ├── init_databases.py           # Initialize PostgreSQL tables, Neo4j constraints
    ├── seed_data.py                # Load sample enterprise documents
    └── generate_embeddings.py      # Batch embed all documents
```

### 1.3 Python Dependencies (requirements-base.txt)
```
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.30.0

# Slack
slack-bolt==1.20.0
slack-sdk==3.31.0

# AI / ML
torch==2.3.0
transformers==4.42.0
sentence-transformers==3.0.0
scikit-learn==1.5.0
prophet==1.1.5
statsmodels==0.14.2
mlxtend==0.23.0           # Apriori / FP-Growth

# LLM
google-generativeai==0.8.0  # Gemini API
langchain==0.2.0
langchain-google-genai==1.0.0

# Databases
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
neo4j==5.20.0
faiss-cpu==1.8.0

# Kafka
confluent-kafka==2.4.0

# Utilities
pydantic==2.7.0
pydantic-settings==2.3.0
python-dotenv==1.0.1
httpx==0.27.0
python-multipart==0.0.9
PyPDF2==3.0.1
python-docx==1.1.0

# Monitoring
prometheus-client==0.20.0
```

### 1.4 Pre-commit & Code Quality
```bash
pip install black flake8 isort mypy pre-commit
```
Configure `.pre-commit-config.yaml` with black, flake8, isort hooks.

**Deliverable**: A clean, well-structured monorepo pushed to Git.

---

## Day 2 (Tue): Docker & Cloud Native Infrastructure

### 2.1 Base Dockerfile (shared across services)
```dockerfile
# services/api-gateway/Dockerfile (example)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY app/ /app/app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 docker-compose.yml
```yaml
version: '3.9'

services:
  # --- Infrastructure ---
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: km_knowledge_base
      POSTGRES_USER: km_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  neo4j:
    image: neo4j:5.19-community
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"

  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  # --- Application Services ---
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - kafka
    env_file: .env

  t1-prediction:
    build: ./services/t1-prediction
    depends_on:
      - kafka
      - postgres
    env_file: .env

  t2-report-generation:
    build: ./services/t2-report-generation
    depends_on:
      - kafka
      - postgres
    env_file: .env

  t3-knowledge-fusion:
    build: ./services/t3-knowledge-fusion
    depends_on:
      - kafka
      - postgres
    env_file: .env

  t4-consistency-check:
    build: ./services/t4-consistency-check
    depends_on:
      - kafka
      - neo4j
    env_file: .env

  t5-knowledge-discovery:
    build: ./services/t5-knowledge-discovery
    depends_on:
      - kafka
      - neo4j
    env_file: .env

  slack-bot:
    build: ./services/slack-bot
    ports:
      - "3000:3000"
    depends_on:
      - api-gateway
    env_file: .env

  orchestrator:
    build: ./services/orchestrator
    depends_on:
      - kafka
      - postgres
      - neo4j
    env_file: .env

  # --- Monitoring ---
  prometheus:
    image: prom/prometheus:v2.51.0
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  postgres_data:
  neo4j_data:
```

### 2.3 Verify Local Environment
```bash
docker-compose up -d postgres neo4j kafka zookeeper
docker-compose ps   # All containers should be "Up"
```

**Deliverable**: All infrastructure containers running locally. Services can connect to Postgres, Neo4j, and Kafka.

---

## Day 3 (Wed): Database & Knowledge Graph Schema Design

### 3.1 PostgreSQL Schema (Centralized Knowledge Base)

This is the "Base de Connaissances Centralisée" from the architecture diagram, holding both "Données de Référence" and "Métadonnées":

```sql
-- Table: Documents (raw source documents)
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,       -- 'pdf', 'docx', 'txt', 'web'
    source_path     TEXT,
    department      VARCHAR(100),               -- e.g., 'IT', 'HR', 'Finance', 'Marketing'
    uploaded_by     VARCHAR(200),
    uploaded_at     TIMESTAMPTZ DEFAULT NOW(),
    last_updated    TIMESTAMPTZ DEFAULT NOW(),
    content_hash    VARCHAR(64),                -- SHA-256 for change detection
    status          VARCHAR(20) DEFAULT 'active' -- 'active', 'obsolete', 'archived'
);

-- Table: Knowledge Chunks (processed text segments)
CREATE TABLE knowledge_chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       BYTEA,                      -- Serialized vector (or use FAISS externally)
    token_count     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Table: Obsolescence Scores (Task 1 output)
CREATE TABLE obsolescence_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id),
    score           FLOAT NOT NULL,             -- 0.0 (fresh) to 1.0 (obsolete)
    predicted_at    TIMESTAMPTZ DEFAULT NOW(),
    model_version   VARCHAR(50),
    factors         JSONB                       -- {"age_days": 180, "access_frequency": 0.02, ...}
);

-- Table: Update Reports (Task 2 output)
CREATE TABLE update_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type     VARCHAR(50) NOT NULL,       -- 'weekly', 'on_demand', 'alert'
    content_md      TEXT NOT NULL,              -- Markdown report content
    generated_at    TIMESTAMPTZ DEFAULT NOW(),
    posted_to_slack BOOLEAN DEFAULT FALSE,
    slack_channel   VARCHAR(100),
    slack_ts        VARCHAR(50)                 -- Slack message timestamp
);

-- Table: Fusion Events (Task 3 output)
CREATE TABLE fusion_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_chunk_ids UUID[] NOT NULL,           -- Array of merged chunk IDs
    merged_chunk_id  UUID REFERENCES knowledge_chunks(id),
    similarity_score FLOAT,
    method          VARCHAR(50),                -- 'kmeans', 'dbscan', 'llm_merge'
    performed_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Table: Consistency Issues (Task 4 output)
CREATE TABLE consistency_issues (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_a_id      UUID REFERENCES knowledge_chunks(id),
    chunk_b_id      UUID REFERENCES knowledge_chunks(id),
    issue_type      VARCHAR(50),                -- 'contradiction', 'redundancy', 'outdated'
    confidence      FLOAT,
    description     TEXT,
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_by     VARCHAR(50),                -- 'auto', 'human', 'orchestrator'
    detected_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Table: Discovered Relations (Task 5 output)
CREATE TABLE discovered_relations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_a        VARCHAR(300) NOT NULL,
    entity_b        VARCHAR(300) NOT NULL,
    relation_type   VARCHAR(100),               -- 'requires', 'related_to', 'contradicts', etc.
    confidence      FLOAT,
    method          VARCHAR(50),                -- 'ner', 'apriori', 'gnn'
    discovered_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Table: Audit Log (Orchestrator traceability — XAI)
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action          VARCHAR(100) NOT NULL,      -- 'fusion', 'consistency_check', 'alert_sent', etc.
    service         VARCHAR(50) NOT NULL,       -- 't1-prediction', 'orchestrator', etc.
    details         JSONB,                      -- Full context of the decision
    explanation     TEXT,                       -- Human-readable XAI explanation
    performed_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Table: Access Logs (for prediction model training)
CREATE TABLE access_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id),
    user_id         VARCHAR(200),
    action          VARCHAR(20),                -- 'view', 'download', 'search_hit'
    accessed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chunks_document ON knowledge_chunks(document_id);
CREATE INDEX idx_obsolescence_document ON obsolescence_scores(document_id);
CREATE INDEX idx_access_logs_document ON access_logs(document_id);
CREATE INDEX idx_access_logs_time ON access_logs(accessed_at);
CREATE INDEX idx_audit_log_time ON audit_log(performed_at);
```

### 3.2 Neo4j Knowledge Graph Schema

Nodes and relationships map directly to the KM domain:

```cypher
// Constraints
CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT dept_name IF NOT EXISTS FOR (dp:Department) REQUIRE dp.name IS UNIQUE;
CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.id IS UNIQUE;

// Node types:
// (:Document {id, title, department, status, created_at})
// (:Concept {name, type, description})          -- Extracted entities/topics
// (:Department {name})                           -- IT, HR, Finance, Marketing
// (:Employee {id, name, role, department})

// Relationship types:
// (:Document)-[:CONTAINS_CONCEPT {confidence}]->(:Concept)
// (:Document)-[:BELONGS_TO]->(:Department)
// (:Concept)-[:RELATED_TO {weight, method}]->(:Concept)
// (:Concept)-[:CONTRADICTS {confidence}]->(:Concept)
// (:Employee)-[:AUTHORED]->(:Document)
// (:Employee)-[:WORKS_IN]->(:Department)
// (:Document)-[:SUPERSEDES]->(:Document)         -- When a doc replaces another
// (:Concept)-[:DERIVED_FROM]->(:Concept)         -- Discovered by Task 5
```

### 3.3 Initialize Databases
To initialize the PostgreSQL tables and Neo4j constraints inside the running Docker cluster, run the appropriate command for your terminal:

- **Linux / macOS / Windows Git Bash:**
  ```bash
  docker compose exec -T api-gateway python - < scripts/init_databases.py
  ```

- **Windows PowerShell:**
  ```powershell
  Get-Content .\scripts\init_databases.py -Raw | docker compose exec -T api-gateway python -
  ```

- **Windows Command Prompt (CMD):**
  ```cmd
  docker compose exec -T api-gateway python - < scripts/init_databases.py
  ```

**Deliverable**: Both databases initialized with schemas and constraints, accessible from Python.

---

## Day 4 (Thu): Data Ingestion & NLP Preprocessing Pipeline

### 4.1 Document Parser Module (`shared/parsers/`)

Supports the document types found in enterprise environments (as referenced in Ikram's memoir: PDF, DOCX, Excel, images):

```python
# shared/parsers/document_parser.py
class DocumentParser:
    """Parses PDF, DOCX, and TXT files into raw text."""

    def parse(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        elif ext == '.txt':
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
```

### 4.2 Text Chunking Strategy

Using recursive character text splitting (LangChain-style) with overlap to preserve context across chunk boundaries:

```python
# shared/chunking/splitter.py
class KnowledgeChunkSplitter:
    """Splits documents into semantic chunks suitable for embedding."""

    def __init__(self, chunk_size=512, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        # Recursive splitting: paragraphs → sentences → characters
        ...
```

**Configuration rationale**: 
- `chunk_size=512` tokens — Matches the max input of `all-MiniLM-L6-v2` (256 word-pieces ≈ 512 characters), which keeps embeddings contextually rich.
- `chunk_overlap=50` — Prevents information loss at chunk boundaries.

### 4.3 Ingestion API Endpoint

```python
# services/api-gateway/app/routes/ingest.py
@router.post("/ingest")
async def ingest_document(file: UploadFile, department: str, uploaded_by: str):
    """
    1. Save file to storage
    2. Parse text from file
    3. Chunk text
    4. Store document metadata in PostgreSQL
    5. Publish 'document.ingested' event to Kafka
    """
```

**Deliverable**: A working ingestion endpoint that parses files and stores chunks in PostgreSQL.

---

## Day 5 (Fri): Embedding Generation & Vector Storage

### 5.1 Embedding Model Selection

| Model                        | Dimensions | Speed   | Quality | Choice Rationale                                      |
|------------------------------|-----------|---------|---------|-------------------------------------------------------|
| `all-MiniLM-L6-v2`          | 384       | Fast    | Good    | Lightweight, runs locally even without GPU             |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Medium | Good | Supports French documents (enterprise context)         |
| OpenAI `text-embedding-3-small` | 1536   | API     | Excellent| Best quality but requires API key and internet access |

**Primary choice**: `paraphrase-multilingual-MiniLM-L12-v2` — because enterprise documents in Algeria may be in French and/or Arabic, this model supports both.

### 5.2 Embedding Pipeline

```python
# shared/embeddings/encoder.py
from sentence_transformers import SentenceTransformer

class KnowledgeEncoder:
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)
```

### 5.3 FAISS Index Setup

```python
# shared/database/vector_store.py
import faiss

class VectorStore:
    def __init__(self, dimension=384):
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine on normalized)
        self.id_map = {}  # faiss_id → chunk_uuid

    def add(self, embeddings: np.ndarray, chunk_ids: list[str]):
        ...

    def search(self, query_embedding: np.ndarray, top_k=5):
        ...

    def save(self, path: str):
        faiss.write_index(self.index, path)
```

### 5.4 Knowledge Graph Population

When a document is ingested and chunked, simultaneously create nodes in Neo4j:

```cypher
// For each ingested document:
MERGE (d:Document {id: $doc_id})
SET d.title = $title, d.department = $dept, d.status = 'active'

MERGE (dp:Department {name: $dept})
MERGE (d)-[:BELONGS_TO]->(dp)

// For each extracted concept (from NER in Day 4 or Task 5):
MERGE (c:Concept {name: $concept_name})
MERGE (d)-[:CONTAINS_CONCEPT {confidence: $conf}]->(c)
```

### 5.5 End-to-End Ingestion Test

Choose the command matching your operating system and shell:

**For Linux / macOS / Windows Git Bash:**
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@data/raw/sample_report.pdf" \
  -F "department=IT" \
  -F "uploaded_by=admin"
```

**For Windows PowerShell:**
```powershell
curl.exe -X POST http://localhost:8000/ingest `
  -F "file=@data/raw/sample_report.pdf" `
  -F "department=IT" `
  -F "uploaded_by=admin"
```

**For Windows Command Prompt (CMD):**
```cmd
curl -X POST http://localhost:8000/ingest ^
  -F "file=@data/raw/sample_report.pdf" ^
  -F "department=IT" ^
  -F "uploaded_by=admin"
```

# Verify:
# 1. Document record in PostgreSQL ✓
# 2. Knowledge chunks in PostgreSQL ✓
# 3. Embeddings in FAISS index ✓
# 4. Document node + Department node in Neo4j ✓
# 5. 'document.ingested' event in Kafka ✓

**Deliverable**: Complete data ingestion pipeline — from raw file upload to searchable embeddings and graph nodes.

---

## Weekend (Sat–Sun): Buffer, Testing & Dataset Preparation

### Tasks:
1. **Unit tests** for parser, chunker, encoder, and vector store.
2. **Prepare test datasets**:
   - Collect/generate 20–30 sample enterprise documents (technical procedures, HR policies, financial reports) in French.
   - Ensure some documents are deliberately redundant (for T3 testing).
   - Ensure some documents contain contradictions (for T4 testing).
   - Ensure some documents are "old" with timestamps from 2+ years ago (for T1 testing).
3. **Run batch ingestion** to populate the databases for Week 2 development.
4. **Code review**: Clean up, add docstrings, commit to Git.

### Week 1 Exit Criteria:
- [ ] Docker Compose brings up all infrastructure (Postgres, Neo4j, Kafka, Zookeeper).
- [ ] API Gateway accepts document uploads and returns 200 OK.
- [ ] Documents are parsed, chunked, embedded, and stored in both Postgres and FAISS.
- [ ] Knowledge Graph has Document and Department nodes.
- [ ] Kafka topic `document.ingested` receives messages.
- [ ] At least 20 test documents are ingested into the system.
