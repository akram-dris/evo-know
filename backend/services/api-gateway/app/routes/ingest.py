import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, Document, KnowledgeChunk, User
from app.auth import require_role, get_current_user
from shared.parsers.document_parser import DocumentParser
from shared.chunking.splitter import KnowledgeChunkSplitter
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.vector_store import VectorStore
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.neo4j_client import Neo4jClient

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])
parser = DocumentParser()
splitter = KnowledgeChunkSplitter()
encoder = KnowledgeEncoder()
vector_store = VectorStore()
kafka_producer = KafkaProducerWrapper()
neo4j_client = Neo4jClient()

@router.post("")
async def ingest_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    uploaded_by: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Ingests a raw document (PDF, DOCX, TXT):
    1. Saves file to local storage
    2. Parses text from file
    3. Chunks text into 512 token segments
    4. Generates embeddings
    5. Stores metadata & chunks in PostgreSQL
    6. Stores vectors in FAISS
    7. Creates Neo4j nodes
    8. Publishes 'document.ingested' event to Kafka
    """
    print(f"📥 [Ingestion] Processing file: {file.filename}")
    # 1. Save file
    os.makedirs("/data/raw", exist_ok=True)
    file_path = f"/data/raw/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Parse text
    try:
        text_content = parser.parse(file_path)
    except Exception as e:
        print(f"❌ [Ingestion] Parsing failed for {file.filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {e}")
        
    # 3. Create Document record in Postgres
    doc = Document(
        title=file.filename,
        source_type=file.filename.split(".")[-1].lower(),
        source_path=file_path,
        department=department,
        uploaded_by=uploaded_by
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 4. Chunk text
    chunks = splitter.split(text_content)
    if not chunks:
        print(f"❌ [Ingestion] No extractable text in {file.filename}")
        raise HTTPException(status_code=400, detail="Document contains no extractable text.")
        
    # 5. Generate embeddings & store chunks
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
        
    # 6. Store in FAISS
    vector_store.add(embeddings, chunk_uuids)
    
    # 7. Create Neo4j nodes
    cypher_query = """
    MERGE (d:Document {id: $doc_id})
    SET d.title = $title, d.department = $dept, d.status = 'active'
    MERGE (dp:Department {name: $dept})
    MERGE (d)-[:BELONGS_TO]->(dp)
    """
    neo4j_client.run_query(cypher_query, {
        "doc_id": str(doc.id),
        "title": doc.title,
        "dept": doc.department
    })
    
    # 8. Publish Kafka event
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
        "message": "Document successfully ingested, embedded, and indexed."
    }

def rebuild_faiss_index(db: Session):
    import numpy as np
    vector_store.reset()
    chunks = db.query(KnowledgeChunk).join(Document).filter(Document.status == "active").all()
    if not chunks:
        return
        
    embeddings = []
    chunk_ids = []
    for c in chunks:
        if c.embedding:
            emb = np.frombuffer(c.embedding, dtype=np.float32)
            embeddings.append(emb)
            chunk_ids.append(str(c.id))
            
    if embeddings:
        embeddings_np = np.vstack(embeddings)
        vector_store.add(embeddings_np, chunk_ids)

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Expert"]))
):
    """
    Delete a document and all its chunks from PostgreSQL, Neo4j, raw files, and FAISS.
    """
    from uuid import UUID
    try:
        doc_uuid = UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    doc = db.query(Document).filter(Document.id == doc_uuid).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
        
    # Delete from Neo4j
    try:
        cypher_query = "MATCH (d:Document {id: $doc_id}) DETACH DELETE d"
        neo4j_client.run_query(cypher_query, {"doc_id": str(doc.id)})
    except Exception as ne:
        print(f"Warning: Failed to delete Neo4j node for doc {doc_id}: {ne}")
        
    # Delete raw file from disk
    if doc.source_path and os.path.exists(doc.source_path):
        try:
            os.remove(doc.source_path)
        except Exception as fe:
            print(f"Warning: Failed to remove file from disk: {fe}")
            
    # Delete from Postgres (cascading automatically deletes knowledge_chunks and scores)
    db.delete(doc)
    db.commit()
    
    # Rebuild FAISS index
    try:
        rebuild_faiss_index(db)
    except Exception as fe:
        print(f"Warning: Failed to rebuild FAISS index: {fe}")
        
    return {
        "status": "success",
        "message": f"Document '{doc.title}' et toutes les données associées ont été supprimés."
    }
