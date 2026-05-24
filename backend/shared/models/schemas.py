from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    title: str
    department: str
    uploaded_by: str

class DocumentCreate(DocumentBase):
    source_type: str
    source_path: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    status: str
    uploaded_at: datetime
    last_updated: datetime

class KnowledgeChunkBase(BaseModel):
    chunk_index: int
    content: str
    token_count: int

class KnowledgeChunkResponse(KnowledgeChunkBase):
    id: UUID
    document_id: UUID
    created_at: datetime

class ObsolescenceScoreBase(BaseModel):
    document_id: UUID
    score: float
    factors: dict

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5

class WebhookRegistration(BaseModel):
    url: str
    events: List[str]
    secret: str
