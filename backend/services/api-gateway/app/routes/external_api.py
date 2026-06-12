import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import create_api_token, verify_token
from shared.database.postgres import get_db, Document, KnowledgeChunk, Webhook
from shared.database.neo4j_client import Neo4jClient
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder
from shared.chunking.splitter import KnowledgeChunkSplitter
from shared.kafka.producer import KafkaProducerWrapper
from app.routes.query import handle_query, QueryRequest

router = APIRouter(prefix="/api/v1/external", tags=["External Interoperability"])

# Initializing wrappers
splitter = KnowledgeChunkSplitter()
encoder = KnowledgeEncoder()
vector_store = VectorStore()
kafka_producer = KafkaProducerWrapper()
neo4j_client = Neo4jClient()

# Schemas
class TokenRequest(BaseModel):
    client_name: str
    scopes: Optional[List[str]] = []

class ExternalDocumentPush(BaseModel):
    title: str
    department: str
    uploaded_by: str
    content: str

class WebhookRegistration(BaseModel):
    url: str
    events: List[str]
    secret: str

@router.post("/token", response_model=dict)
async def generate_token(request: TokenRequest):
    """
    Public endpoint to generate a JWT token for external system clients.
    """
    token = create_api_token(request.client_name, request.scopes)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_days": 365
    }

@router.get("/documents", response_model=List[dict])
async def list_documents(
    department: Optional[str] = None,
    status_filter: Optional[str] = "active",
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    JWT protected endpoint for external systems to fetch knowledge documents.
    """
    query = db.query(Document)
    if department:
        query = query.filter(Document.department == department)
    if status_filter:
        query = query.filter(Document.status == status_filter)
        
    docs = query.order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "source_type": d.source_type,
            "department": d.department,
            "uploaded_by": d.uploaded_by,
            "uploaded_at": d.uploaded_at.isoformat(),
            "status": d.status
        }
        for d in docs
    ]

@router.post("/documents", response_model=dict)
async def push_document(
    doc_payload: ExternalDocumentPush,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    JWT protected endpoint for external systems to push raw knowledge documents.
    Triggers the entire ingestion, chunking, vector, graph and Kafka pipeline.
    """
    # 1. Save metadata to Postgres
    doc = Document(
        title=doc_payload.title,
        source_type="text",
        source_path="api-ingest",
        department=doc_payload.department,
        uploaded_by=doc_payload.uploaded_by,
        status="active"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 2. Chunk text content
    chunks = splitter.split(doc_payload.content)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content contains no extractable text."
        )

    # 3. Generate embeddings & save chunks to Postgres
    embeddings = encoder.encode(chunks)
    chunk_uuids = []
    
    for idx, chunk_text in enumerate(chunks):
        kc = KnowledgeChunk(
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_text,
            token_count=len(chunk_text.split()),
            embedding=embeddings[idx].tobytes()
        )
        db.add(kc)
        db.commit()
        db.refresh(kc)
        chunk_uuids.append(str(kc.id))

    # 4. Store in FAISS
    vector_store.add(embeddings, chunk_uuids)

    # 5. Create Neo4j nodes
    cypher_query = """
    MERGE (d:Document {id: $doc_id})
    SET d.title = $title, d.department = $dept, d.status = 'active'
    MERGE (dp:Department {name: $dept})
    MERGE (d)-[:BELONGS_TO]->(dp)
    """
    try:
        neo4j_client.run_query(cypher_query, {
            "doc_id": str(doc.id),
            "title": doc.title,
            "dept": doc.department
        })
    except Exception as e:
        print(f"⚠️ Neo4j insertion failed in external_api: {e}")

    # 6. Publish Kafka event
    kafka_producer.publish("document.ingested", {
        "document_id": str(doc.id),
        "title": doc.title,
        "department": doc.department,
        "uploaded_by": doc.uploaded_by,
        "chunks_count": len(chunks)
    })

    return {
        "status": "success",
        "document_id": str(doc.id),
        "chunks_created": len(chunks),
        "message": "Document successfully pushed, ingested, embedded and indexed."
    }

@router.post("/query")
async def semantic_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    JWT protected semantic query (RAG) endpoint for external intranet or mobile systems.
    """
    return await handle_query(request, db)

@router.get("/concepts", response_model=List[dict])
async def list_concepts(
    related_to: Optional[str] = None,
    token: dict = Depends(verify_token)
):
    """
    JWT protected endpoint to query concepts and relations from the Neo4j Knowledge Graph.
    """
    if related_to:
        query = """
        MATCH (c1:Concept {name: $name})-[r]->(c2:Concept)
        RETURN c1.name AS source, type(r) AS relation, c2.name AS target
        """
        results = neo4j_client.run_query(query, {"name": related_to})
    else:
        query = """
        MATCH (c:Concept)
        RETURN c.name AS name, labels(c) AS types LIMIT 100
        """
        results = neo4j_client.run_query(query)
    return results

@router.post("/webhooks/register", response_model=dict)
async def register_webhook(
    registration: WebhookRegistration,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    JWT protected endpoint for external systems to register to receive push webhook events.
    """
    webhook = Webhook(
        url=registration.url,
        events=registration.events,
        secret=registration.secret
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return {
        "id": str(webhook.id),
        "status": "registered",
        "url": webhook.url,
        "events": webhook.events
    }
