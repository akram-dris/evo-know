import os
import sys
import time
import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception:
    pass

# PostgreSQL Config
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "km_knowledge_base")
PG_USER = os.getenv("POSTGRES_USER", "km_admin")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "km_secure_password_2026")

# Neo4j Config
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_2026")

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,
    source_path     TEXT,
    department      VARCHAR(100),
    uploaded_by     VARCHAR(200),
    uploaded_at     TIMESTAMPTZ DEFAULT NOW(),
    last_updated    TIMESTAMPTZ DEFAULT NOW(),
    content_hash    VARCHAR(64),
    status          VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       BYTEA,
    token_count     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS obsolescence_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id) ON DELETE CASCADE,
    score           FLOAT NOT NULL,
    predicted_at    TIMESTAMPTZ DEFAULT NOW(),
    model_version   VARCHAR(50),
    factors         JSONB
);

CREATE TABLE IF NOT EXISTS update_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type     VARCHAR(50) NOT NULL,
    content_md      TEXT NOT NULL,
    generated_at    TIMESTAMPTZ DEFAULT NOW(),
    posted_to_slack BOOLEAN DEFAULT FALSE,
    slack_channel   VARCHAR(100),
    slack_ts        VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS fusion_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_chunk_ids UUID[] NOT NULL,
    merged_chunk_id  UUID REFERENCES knowledge_chunks(id) ON DELETE SET NULL,
    similarity_score FLOAT,
    method          VARCHAR(50),
    performed_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consistency_issues (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_a_id      UUID REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    chunk_b_id      UUID REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    issue_type      VARCHAR(50),
    confidence      FLOAT,
    description     TEXT,
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_by     VARCHAR(50),
    detected_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS discovered_relations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_a        VARCHAR(300) NOT NULL,
    entity_b        VARCHAR(300) NOT NULL,
    relation_type   VARCHAR(100),
    confidence      FLOAT,
    method          VARCHAR(50),
    discovered_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action          VARCHAR(100) NOT NULL,
    service         VARCHAR(50) NOT NULL,
    details         JSONB,
    explanation     TEXT,
    performed_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS access_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id         VARCHAR(200),
    action          VARCHAR(20),
    accessed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document ON knowledge_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_obsolescence_document ON obsolescence_scores(document_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_document ON access_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_time ON access_logs(accessed_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_time ON audit_log(performed_at);
"""

CYPHER_CONSTRAINTS = [
    "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;",
    "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;",
    "CREATE CONSTRAINT dept_name IF NOT EXISTS FOR (dp:Department) REQUIRE dp.name IS UNIQUE;",
    "CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.id IS UNIQUE;"
]

def init_postgres():
    print(f"🔄 Connecting to PostgreSQL at {PG_HOST}:{PG_PORT}...")
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASS
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                print("⚡ Executing PostgreSQL schema creation...")
                cur.execute(SQL_SCHEMA)
            conn.close()
            print("✅ PostgreSQL tables and indexes initialized successfully.")
            return
        except Exception as e:
            print(f"⚠️ PostgreSQL connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("❌ Fatal: Could not connect to PostgreSQL.")
                sys.exit(1)
            time.sleep(3)

def init_neo4j():
    print(f"🔄 Connecting to Neo4j at {NEO4J_URI}...")
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
            driver.verify_connectivity()
            with driver.session() as session:
                print("⚡ Executing Neo4j constraints creation...")
                for constraint in CYPHER_CONSTRAINTS:
                    session.run(constraint)
            driver.close()
            print("✅ Neo4j constraints initialized successfully.")
            return
        except Exception as e:
            print(f"⚠️ Neo4j connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("❌ Fatal: Could not connect to Neo4j.")
                sys.exit(1)
            time.sleep(3)

if __name__ == "__main__":
    print("🚀 Starting Database Initialization Script...")
    init_postgres()
    init_neo4j()
    print("🎉 All databases initialized successfully!")
