import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, Document, KnowledgeChunk
from shared.parsers.document_parser import DocumentParser
from shared.chunking.splitter import KnowledgeChunkSplitter
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.vector_store import VectorStore
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.neo4j_client import Neo4jClient

router = APIRouter(prefix="/ingest", tags=["Ingestion"])
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
    # 1. Save file
    os.makedirs("/data/raw", exist_ok=True)
    file_path = f"/data/raw/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Parse text
    try:
        text_content = parser.parse(file_path)
    except Exception as e:
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
