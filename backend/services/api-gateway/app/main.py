from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, ingest, query, alerts, audit, reports, external_api, auth_routes, dashboard, tasks_api

def rebuild_faiss_on_startup():
    """Rebuild FAISS index from PostgreSQL chunks if the index is empty (e.g. after container restart)."""
    try:
        import numpy as np
        from shared.database.vector_store import VectorStore
        from shared.embeddings.encoder import KnowledgeEncoder
        from shared.database.postgres import SessionLocal, KnowledgeChunk

        vs = VectorStore()
        if vs.index.ntotal > 0:
            print(f"✅ FAISS index already loaded with {vs.index.ntotal} vectors.")
            return

        print("⚠️  FAISS index is empty — rebuilding from PostgreSQL...")
        db = SessionLocal()
        chunks = db.query(KnowledgeChunk.id, KnowledgeChunk.content).all()
        db.close()

        if not chunks:
            print("ℹ️  No chunks in database yet. FAISS index will be built on first upload.")
            return

        encoder = KnowledgeEncoder()
        vs.reset()
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.content for c in batch]
            ids = [str(c.id) for c in batch]
            embeddings = encoder.encode(texts)
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            vs.add(embeddings, ids)
        print(f"✅ FAISS index rebuilt successfully — {vs.index.ntotal} vectors indexed.")
    except Exception as e:
        print(f"❌ FAISS rebuild error on startup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    rebuild_faiss_on_startup()
    yield

app = FastAPI(
    title="KM API Gateway",
    description="Single entry point for the Cloud Native Knowledge Management Update System.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(alerts.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(external_api.router)
app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(tasks_api.router)

@app.get("/")
async def root():
    return {
        "service": "api-gateway",
        "status": "operational",
        "documentation": "/docs"
    }
