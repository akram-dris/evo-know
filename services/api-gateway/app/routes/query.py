from fastapi import APIRouter, Depends, HTTPException
from shared.models.schemas import QueryRequest
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder
from shared.database.postgres import get_db, KnowledgeChunk, Document
from sqlalchemy.orm import Session

router = APIRouter(prefix="/query", tags=["Query"])
encoder = KnowledgeEncoder()
vector_store = VectorStore()

@router.post("")
async def search_knowledge(query: QueryRequest, db: Session = Depends(get_db)):
    """Semantic search endpoint returning top-K relevant knowledge chunks."""
    query_embedding = encoder.encode([query.question])[0]
    results = vector_store.search(query_embedding, top_k=query.top_k or 5)
    
    enriched_results = []
    for res in results:
        chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == res["id"]).first()
        if chunk:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            enriched_results.append({
                "chunk_id": str(chunk.id),
                "document_title": doc.title if doc else "Unknown",
                "department": doc.department if doc else "Unknown",
                "content": chunk.content,
                "similarity_score": res["score"]
            })
            
    return {
        "query": query.question,
        "top_k": query.top_k,
        "results": enriched_results
    }
