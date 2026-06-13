import os
import sys
import time
import psycopg2
import hashlib
from neo4j import GraphDatabase
from dotenv import load_dotenv

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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

CREATE TABLE IF NOT EXISTS webhooks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url             VARCHAR(1000) NOT NULL,
    events          VARCHAR(100)[] NOT NULL,
    secret          VARCHAR(500) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(300) NOT NULL,
    email           VARCHAR(255),
    role            VARCHAR(50) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
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
                
                print("🌱 Seeding default users (Admin, Expert, Reader)...")
                users_data = [
                    ("admin", get_password_hash("admin_pass_2026"), "admin@evoknow.com", "Admin"),
                    ("expert", get_password_hash("expert_pass_2026"), "expert@evoknow.com", "Expert"),
                    ("reader", get_password_hash("reader_pass_2026"), "reader@evoknow.com", "Reader")
                ]
                for username, pwd_hash, email, role in users_data:
                    cur.execute(
                        """
                        INSERT INTO users (username, password_hash, email, role)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (username) DO NOTHING;
                        """,
                        (username, pwd_hash, email, role)
                    )

                # Check if data already exists to prevent duplicate seeding
                cur.execute("SELECT COUNT(*) FROM documents;")
                if cur.fetchone()[0] == 0:
                    print("🌱 Seeding demonstration data (Documents, Chunks, Scores, Contradictions, Relations)...")
                    
                    # 1. Seed Documents
                    docs = [
                        ("OSS-4G-Procedure-v2", "pdf", "/data/raw/OSS-4G-Procedure-v2.pdf", "IT Support", "Akram Dris", "active"),
                        ("Backup-Policy-2025", "docx", "/data/raw/Backup-Policy-2025.docx", "Infrastructure", "Asma", "active"),
                        ("Security-Protocol-v1", "txt", "/data/raw/Security-Protocol-v1.txt", "Security", "TestUser", "active"),
                        ("Cloud-Architecture-Specs", "pdf", "/data/raw/Cloud-Architecture-Specs.pdf", "R&D", "Admin", "active")
                    ]
                    doc_ids = []
                    for title, src_type, src_path, dept, uploaded_by, status in docs:
                        cur.execute(
                            """
                            INSERT INTO documents (title, source_type, source_path, department, uploaded_by, status)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id;
                            """,
                            (title, src_type, src_path, dept, uploaded_by, status)
                        )
                        doc_ids.append(cur.fetchone()[0])

                    # 2. Seed Knowledge Chunks
                    chunks = [
                        (doc_ids[0], 0, "Cette procédure décrit le déploiement du réseau d'accès radio 4G LTE. Le processus nécessite l'arrêt périodique des émetteurs-récepteurs toutes les 24 heures pour effectuer l'étalonnage thermique."),
                        (doc_ids[1], 0, "Politique de sauvegarde de l'infrastructure: Sauvegarde incrémentielle quotidienne programmée chaque nuit à 02:00 du matin. Les données sont répliquées vers le serveur secondaire."),
                        (doc_ids[2], 0, "Protocole de sécurité général: Toutes les sauvegardes de serveurs de production doivent s'exécuter strictement à 04:00 du matin pour éviter les pics de charge réseau et les conflits d'accès."),
                        (doc_ids[3], 0, "Spécifications de l'architecture cloud native: Utilisation de Kubernetes pour l'orchestration des conteneurs Docker, avec API Gateway FastAPI et bus d'événements Kafka.")
                    ]
                    chunk_ids = []
                    for doc_id, idx, content in chunks:
                        cur.execute(
                            """
                            INSERT INTO knowledge_chunks (document_id, chunk_index, content, token_count)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id;
                            """,
                            (doc_id, idx, content, len(content.split()))
                        )
                        chunk_ids.append(cur.fetchone()[0])

                    # 3. Seed Obsolescence Scores
                    scores = [
                        (doc_ids[0], 0.85, '{"age_factor": 0.9, "access_decline": 0.8}'),
                        (doc_ids[1], 0.32, '{"age_factor": 0.2, "access_decline": 0.4}'),
                        (doc_ids[2], 0.72, '{"age_factor": 0.8, "access_decline": 0.6}'),
                        (doc_ids[3], 0.15, '{"age_factor": 0.1, "access_decline": 0.2}')
                    ]
                    for doc_id, score, factors_json in scores:
                        cur.execute(
                            """
                            INSERT INTO obsolescence_scores (document_id, score, model_version, factors)
                            VALUES (%s, %s, 'Ensemble-LSTM-Prophet-v1', %s);
                            """,
                            (doc_id, score, factors_json)
                        )

                    # 4. Seed Consistency Issues (T4 Contradictions)
                    # Contradiction between Backup-Policy-2025 (Daily at 2AM) and Security-Protocol-v1 (Daily at 4AM)
                    cur.execute(
                        """
                        INSERT INTO consistency_issues (chunk_a_id, chunk_b_id, issue_type, confidence, description, resolved)
                        VALUES (%s, %s, 'Contradiction', 0.88, 'Conflit de planification de sauvegarde détecté : Daily at 02:00 vs Daily at 04:00.', FALSE);
                        """,
                        (chunk_ids[1], chunk_ids[2])
                    )

                    # 5. Seed Discovered Relations (T5 Relations)
                    relations = [
                        ("Kubernetes", "Docker", "DEPENDS_ON", 0.92, "NER+Apriori"),
                        ("FastAPI", "Uvicorn", "RUNS_ON", 0.98, "NER+Apriori"),
                        ("Kafka", "ZooKeeper", "DEPENDS_ON", 0.95, "NER+Apriori")
                    ]
                    for ent_a, ent_b, rel_type, conf, method in relations:
                        cur.execute(
                            """
                            INSERT INTO discovered_relations (entity_a, entity_b, relation_type, confidence, method)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (ent_a, ent_b, rel_type, conf, method)
                        )

                    # 6. Seed Fusion Events (T3 Merges)
                    cur.execute(
                        """
                        INSERT INTO fusion_events (source_chunk_ids, merged_chunk_id, similarity_score, method)
                        VALUES (%s::uuid[], %s, 0.91, 'DBSCAN-LLM');
                        """,
                        ([chunk_ids[0], chunk_ids[1]], chunk_ids[3])
                    )

                    # 7. Seed Audit Logs (XAI explanations)
                    audit_logs = [
                        ("document_ingestion_orchestrated", "orchestrator", '{"title": "Cloud-Architecture-Specs"}', "Nouveau document 'Cloud-Architecture-Specs' ingéré pour 'R&D'. L'orchestrateur déclenche les processus d'extraction et de calcul."),
                        ("prediction_scored_orchestrated", "orchestrator", '{"score": 0.85}', "Score d'obsolescence (T1) calculé pour le document OSS-4G-Procedure-v2: 0.85. Alerte d'obsolescence élevée transmise au tableau de bord."),
                        ("consistency_checked_orchestrated", "orchestrator", '{"conflicts_found_count": 1}', "Étape Vérification de Cohérence (T4) terminée. 1 contradiction textuelle identifiée entre Backup-Policy-2025 et Security-Protocol-v1."),
                        ("fusion_orchestrated", "orchestrator", '{"merged_chunk_id": "'+str(chunk_ids[3])+'"}', "Étape Fusion Sémantique (T3) terminée. L'orchestrateur a fusionné 2 fragments de connaissances redondants dans R&D."),
                        ("discovery_orchestrated", "orchestrator", '{"new_relations_count": 3}', "Nouvelles connaissances découvertes (T5). 3 relations d'association extraites via Apriori et NER.")
                    ]
                    for action, service, details, explanation in audit_logs:
                        cur.execute(
                            """
                            INSERT INTO audit_log (action, service, details, explanation)
                            VALUES (%s, %s, %s, %s);
                            """,
                            (action, service, details, explanation)
                        )
            conn.close()
            print("✅ PostgreSQL tables and indexes initialized & seeded successfully.")
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
