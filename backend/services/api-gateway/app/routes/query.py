import json
from fastapi import APIRouter, Depends, HTTPException, Request
from shared.models.schemas import QueryRequest
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.postgres import get_db, KnowledgeChunk, Document
from sqlalchemy.orm import Session
import httpx
import os

router = APIRouter(prefix="/api/v1/query", tags=["Query"])
encoder = KnowledgeEncoder()
vector_store = VectorStore()

# Configure GitHub Models client
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")

def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    """Builds a RAG prompt from the user's question and retrieved knowledge chunks."""
    context = "\n---\n".join([c["content"] for c in chunks])
    return f"Context:\n{context}\n\nQuestion: {question}"

def compute_confidence_score(chunks: list[dict]) -> float:
    """Computes a simple confidence score based on the similarity of retrieved chunks."""
    if not chunks:
        return 0.0
    # Average similarity score of the top chunks
    total_similarity = sum(c["similarity_score"] for c in chunks)
    return total_similarity / len(chunks)

@router.post("")
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Semantic search endpoint that generates contextual answers using RAG.
    1. Retrieve similarity vectors from FAISS.
    2. Retrieve raw source chunks from PostgreSQL.
    3. Generate contextual answer via Ollama.
    4. Return formatted JSON response with citations.
    """
    query_embedding = encoder.encode([request.question])[0]
    
    # 1. Retrieve similarity vectors from FAISS (and their chunk IDs)
    faiss_results = vector_store.search(query_embedding, top_k=request.top_k or 5)
    
    # 2. Retrieve raw source chunks from PostgreSQL
    retrieved_chunks = []
    source_documents = {}  # maps doc_id to title to deduplicate
    for res in faiss_results:
        chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == res["id"]).first()
        if chunk:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            if doc:
                retrieved_chunks.append({
                    "content": chunk.content,
                    "document_title": doc.title,
                    "similarity_score": res["score"]
                })
                source_documents[str(doc.id)] = doc.title
    
    if not retrieved_chunks:
        return {
            "answer": "I cannot find relevant information in the knowledge base.",
            "sources": [],
            "confidence": 0.0
        }

    # 3. Generate contextual answer via GitHub Models API
    rag_prompt = build_rag_prompt(request.question, retrieved_chunks)
    try:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        system_prompt = (
            "You are an intelligent assistant that answers questions based on the provided context only.\n"
            "If the answer is not in the context, state \"I cannot answer this question based on the provided information.\""
        )
        payload = {
            "messages": [
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": rag_prompt }
            ],
            "model": GITHUB_MODEL,
            "temperature": 0.2
        }
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.post(
                "https://models.github.ai/inference/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            err_json = e.response.json()
            if "error" in err_json and "message" in err_json["error"]:
                error_detail = err_json["error"]["message"]
        except Exception:
            pass
        print(f"HTTP status error calling GitHub Models API: {e.response.status_code} - {e.response.text}")
        answer = f"LLM API Error ({e.response.status_code}): {error_detail}"
    except Exception as e:
        print(f"Error calling GitHub Models API: {e}")
        answer = f"LLM Connection Error ({type(e).__name__}): {str(e)}"

    # 4. Return formatted JSON response with citations and confidence
    confidence = compute_confidence_score(retrieved_chunks)
    
    return {
        "answer": answer,
        "sources": [{"id": doc_id, "title": title} for doc_id, title in source_documents.items()],
        "confidence": confidence
    }

@router.get("/documents")
async def get_all_documents(limit: int = 10, offset: int = 0, search: str = None, department: str = None, db: Session = Depends(get_db)):
    """
    Get the list of all active documents in the database.
    """
    query = db.query(Document).filter(Document.status == "active")
    if search:
        query = query.filter(
            (Document.title.ilike(f"%{search}%")) |
            (Document.uploaded_by.ilike(f"%{search}%"))
        )
    if department and department != "Tous":
        query = query.filter(Document.department == department)
        
    query = query.order_by(Document.uploaded_at.desc())
    total = query.count()
    docs = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": str(d.id),
                "title": d.title,
                "source_type": d.source_type,
                "department": d.department,
                "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d") if d.uploaded_at else None,
                "uploaded_by": d.uploaded_by,
                "status": d.status
            }
            for d in docs
        ]
    }

@router.get("/documents/{doc_id}/content")
async def get_document_content(doc_id: str, db: Session = Depends(get_db)):
    """
    Retrieve and concatenate all text chunks for a given document.
    """
    from uuid import UUID
    try:
        doc_uuid = UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    doc = db.query(Document).filter(Document.id == doc_uuid).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
        
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc_uuid).order_by(KnowledgeChunk.chunk_index).all()
    content = "\n\n".join([c.content for c in chunks])
    
    return {
        "title": doc.title,
        "department": doc.department,
        "uploaded_by": doc.uploaded_by,
        "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M") if doc.uploaded_at else None,
        "content": content
    }
