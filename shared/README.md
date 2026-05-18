# 📦 Shared Python Library (`shared/`)

This directory acts as the foundational internal Python package shared across all microservices in the Monorepo. By centralizing core database connections, ML models, Kafka wrappers, and text processing utilities, it guarantees absolute code reusability and architectural consistency.

```
shared/
├── database/                   # Hybrid Persistence Clients (Postgres, Neo4j, FAISS)
├── embeddings/                 # Sentence-Transformers Vector Encoder Wrapper
├── kafka/                      # Apache Kafka Producer & Consumer Base Wrappers
├── models/                     # Pydantic Data Validation & API Request/Response Schemas
├── parsers/                    # Multi-format Document Parsers (PDF, DOCX, TXT)
└── chunking/                   # Advanced NLP Semantic Token Splitters
```

---

## 🛠️ Core Module Capabilities

### 1. Database Clients (`shared/database/`)
- `postgres.py`: SQLAlchemy session management and ORM models (`Document`, `KnowledgeChunk`, `ObsolescenceScore`, `AuditLog`).
- `neo4j_client.py`: Official Neo4j Python driver wrapper managing Cypher queries, graph node creation, and relationship mapping.
- `vector_store.py`: High-speed FAISS vector index wrapper handling sub-millisecond dense embedding storage and similarity search (`top_k`).

### 2. Machine Learning & NLP (`shared/embeddings/` & `shared/chunking/`)
- `encoder.py`: Wraps `sentence-transformers/all-MiniLM-L6-v2` to convert text chunks into 384-dimensional dense vectors.
- `splitter.py`: Splits raw document text into precise 512-token semantic chunks while preserving paragraph boundaries.

### 3. Event-Driven Messaging (`shared/kafka/`)
- `producer.py` & `consumer.py`: Confluent Kafka Python wrappers handling automatic serialization, topic subscription, and robust error recovery.

---

## 💻 Local Development & Importing

Because `shared` is mounted directly into `/app/shared` inside every Docker container, microservices can import its modules seamlessly:

```python
from shared.database.postgres import get_db, Document
from shared.embeddings.encoder import KnowledgeEncoder
from shared.kafka.producer import KafkaProducerWrapper
```
