import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA, ARRAY
from datetime import datetime

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "km_knowledge_base")
PG_USER = os.getenv("POSTGRES_USER", "km_admin")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "km_secure_password_2026")

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_path = Column(Text)
    department = Column(String(100))
    uploaded_by = Column(String(200))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String(64))
    status = Column(String(20), default="active")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(BYTEA)
    token_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ObsolescenceScore(Base):
    __tablename__ = "obsolescence_scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    score = Column(Float, nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))
    factors = Column(JSONB)

class UpdateReport(Base):
    __tablename__ = "update_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String(50), nullable=False)
    content_md = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    posted_to_slack = Column(Boolean, default=False)
    slack_channel = Column(String(100))
    slack_ts = Column(String(50))

class FusionEvent(Base):
    __tablename__ = "fusion_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_chunk_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    merged_chunk_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_chunks.id", ondelete="SET NULL"))
    similarity_score = Column(Float)
    method = Column(String(50))
    performed_at = Column(DateTime, default=datetime.utcnow)

class ConsistencyIssue(Base):
    __tablename__ = "consistency_issues"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_a_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_chunks.id", ondelete="CASCADE"))
    chunk_b_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_chunks.id", ondelete="CASCADE"))
    issue_type = Column(String(50))
    confidence = Column(Float)
    description = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String(50))
    detected_at = Column(DateTime, default=datetime.utcnow)

class DiscoveredRelation(Base):
    __tablename__ = "discovered_relations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_a = Column(String(300), nullable=False)
    entity_b = Column(String(300), nullable=False)
    relation_type = Column(String(100))
    confidence = Column(Float)
    method = Column(String(50))
    discovered_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    service = Column(String(50), nullable=False)
    details = Column(JSONB)
    explanation = Column(Text)
    performed_at = Column(DateTime, default=datetime.utcnow)

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    user_id = Column(String(200))
    action = Column(String(20))
    accessed_at = Column(DateTime, default=datetime.utcnow)

class Webhook(Base):
    __tablename__ = "webhooks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(1000), nullable=False)
    events = Column(ARRAY(String), nullable=False)
    secret = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(300), nullable=False)
    email = Column(String(255))
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
