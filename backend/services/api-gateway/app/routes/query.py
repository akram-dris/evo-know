import json
from fastapi import APIRouter, Depends, HTTPException, Request
from shared.models.schemas import QueryRequest
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.postgres import get_db, KnowledgeChunk, Document
from sqlalchemy.orm import Session
import ollama # Import ollama
import os

router = APIRouter(prefix="/api/v1/query", tags=["Query"])
encoder = KnowledgeEncoder()
vector_store = VectorStore()

# Configure Ollama client
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

client = ollama.Client(base_url=OLLAMA_HOST, timeout=300.0)

def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    """Builds a RAG prompt from the user's question and retrieved knowledge chunks."""
    context = "\n---\n".join([c["content"] for c in chunks])
    prompt = f"""
    You are an intelligent assistant that answers questions based on the provided context only.
    If the answer is not in the context, state "I cannot answer this question based on the provided information."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    return prompt

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
    source_document_titles = set()
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
                source_document_titles.add(doc.title)
    
    if not retrieved_chunks:
        return {
            "answer": "I cannot find relevant information in the knowledge base.",
            "sources": [],
            "confidence": 0.0
        }

    # 3. Generate contextual answer via Ollama
    rag_prompt = build_rag_prompt(request.question, retrieved_chunks)
    try:
        response = client.generate(
            model=OLLAMA_MODEL,
            prompt=rag_prompt,
            options={'temperature': 0.2}
        )
        answer = response['response']
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        answer = "I am currently unable to generate an answer using Ollama. Please try again later."

    # 4. Return formatted JSON response with citations and confidence
    confidence = compute_confidence_score(retrieved_chunks)
    
    return {
        "answer": answer,
        "sources": list(source_document_titles),
        "confidence": confidence
    }
