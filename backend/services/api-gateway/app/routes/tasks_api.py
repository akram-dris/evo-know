from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from shared.database.postgres import (
    get_db, Document, ObsolescenceScore, FusionEvent, 
    ConsistencyIssue, DiscoveredRelation, AuditLog
)

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks API"])

class ResolutionRequest(BaseModel):
    choice: str # 'keep_a', 'keep_b', 'merge'
    user: str

@router.get("/predictions")
async def get_predictions(db: Session = Depends(get_db)):
    """
    Get obsolescence score forecasts (T1 results).
    """
    scores = db.query(ObsolescenceScore, Document).join(
        Document, ObsolescenceScore.document_id == Document.id
    ).order_by(ObsolescenceScore.score.desc()).all()
    
    return [
        {
            "id": str(s[0].id),
            "document_id": str(s[0].document_id),
            "title": s[1].title,
            "department": s[1].department,
            "score": s[0].score,
            "predicted_at": s[0].predicted_at.isoformat(),
            "model_version": s[0].model_version,
            "factors": s[0].factors,
            "priority": "Critical" if s[0].score > 0.8 else ("High" if s[0].score > 0.5 else "Normal")
        }
        for s in scores
    ]

@router.get("/fusions")
async def get_fusions(db: Session = Depends(get_db)):
    """
    Get completed semantic fusions (T3 results).
    """
    events = db.query(FusionEvent).order_by(FusionEvent.performed_at.desc()).all()
    return [
        {
            "id": str(e.id),
            "source_chunks": [str(uid) for uid in e.source_chunk_ids],
            "merged_chunk": str(e.merged_chunk_id) if e.merged_chunk_id else None,
            "similarity_score": e.similarity_score,
            "method": e.method,
            "performed_at": e.performed_at.isoformat()
        }
        for e in events
    ]

@router.get("/consistency")
async def get_consistency_issues(db: Session = Depends(get_db)):
    """
    Get structural contradictions / logical conflicts (T4 results).
    """
    issues = db.query(ConsistencyIssue).order_by(ConsistencyIssue.detected_at.desc()).all()
    return [
        {
            "id": str(i.id),
            "chunk_a_id": str(i.chunk_a_id),
            "chunk_b_id": str(i.chunk_b_id),
            "issue_type": i.issue_type,
            "confidence": i.confidence,
            "description": i.description,
            "resolved": i.resolved,
            "resolved_by": i.resolved_by,
            "detected_at": i.detected_at.isoformat()
        }
        for i in issues
    ]

@router.post("/consistency/resolve/{issue_id}")
async def resolve_consistency_issue(
    issue_id: str,
    payload: ResolutionRequest,
    db: Session = Depends(get_db)
):
    """
    Mark a consistency issue as resolved.
    """
    issue = db.query(ConsistencyIssue).filter(ConsistencyIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    issue.resolved = True
    issue.resolved_by = payload.user
    
    # Log to audit trail
    audit = AuditLog(
        action="conflict_resolved_manually",
        service="api-gateway",
        details={"issue_id": issue_id, "resolution": payload.choice},
        explanation=f"Le conflit {issue_id} a été résolu manuellement par {payload.user} (Choix : {payload.choice})."
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "message": "Consistency issue marked as resolved."}

@router.get("/discovery")
async def get_discovered_relations(db: Session = Depends(get_db)):
    """
    Get discovered relations from Apriori/NER (T5 results).
    """
    relations = db.query(DiscoveredRelation).order_by(DiscoveredRelation.discovered_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "entity_a": r.entity_a,
            "entity_b": r.entity_b,
            "relation_type": r.relation_type,
            "confidence": r.confidence,
            "method": r.method,
            "discovered_at": r.discovered_at.isoformat()
        }
        for r in relations
    ]
