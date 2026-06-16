import json
from fastapi import APIRouter, Depends, HTTPException, Request
from shared.models.schemas import QueryRequest
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.postgres import get_db, KnowledgeChunk, Document
from sqlalchemy.orm import Session
import os
import google.generativeai as genai

router = APIRouter(prefix="/api/v1/query", tags=["Query"])
encoder = KnowledgeEncoder()
vector_store = VectorStore()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

    # 3. Generate contextual answer via Google Gemini API
    rag_prompt = build_rag_prompt(request.question, retrieved_chunks)
    try:
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY is not configured in environment variables.")
            
        system_prompt = (
            "You are an intelligent assistant that answers questions based on the provided context only.\n"
            "If the answer is not in the context, state \"I cannot answer this question based on the provided information.\"\n\n"
        )
        
        prompt = system_prompt + rag_prompt
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        answer = f"Gemini API Error ({type(e).__name__}): {str(e)}"

    # 4. Return formatted JSON response with citations and confidence
    confidence = compute_confidence_score(retrieved_chunks)
    
    return {
        "answer": answer,
        "sources": [{"id": doc_id, "title": title} for doc_id, title in source_documents.items()],
        "confidence": confidence
    }

@router.get("/documents")
async def get_all_documents(db: Session = Depends(get_db)):
    """
    Get the list of all active documents in the database.
    """
    docs = db.query(Document).filter(Document.status == "active").order_by(Document.uploaded_at.desc()).all()
    return [
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
