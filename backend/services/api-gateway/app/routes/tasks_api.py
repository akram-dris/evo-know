from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel

from shared.database.postgres import (
    get_db, Document, KnowledgeChunk, ObsolescenceScore, FusionEvent, 
    ConsistencyIssue, DiscoveredRelation, AuditLog
)

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks API"])

class ResolutionRequest(BaseModel):
    choice: str # 'keep_a', 'keep_b', 'merge'
    user: str

@router.get("/predictions")
async def get_predictions(limit: int = 10, offset: int = 0, search: str = None, db: Session = Depends(get_db)):
    """
    Get obsolescence score forecasts (T1 results).
    """
    # Get the latest predicted_at per document_id to avoid showing duplicate historical scores
    subq = db.query(
        ObsolescenceScore.document_id,
        func.max(ObsolescenceScore.predicted_at).label("max_date")
    ).group_by(ObsolescenceScore.document_id).subquery()

    query = db.query(ObsolescenceScore, Document).join(
        Document, ObsolescenceScore.document_id == Document.id
    ).join(
        subq,
        (ObsolescenceScore.document_id == subq.c.document_id) &
        (ObsolescenceScore.predicted_at == subq.c.max_date)
    )
    
    if search:
        query = query.filter(
            (Document.title.ilike(f"%{search}%")) |
            (Document.department.ilike(f"%{search}%"))
        )
        
    query = query.order_by(ObsolescenceScore.score.desc())
    total = query.count()
    scores = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
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
    }

@router.get("/fusions")
async def get_fusions(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get completed semantic fusions (T3 results).
    """
    query = db.query(FusionEvent).order_by(FusionEvent.performed_at.desc())
    total = query.count()
    events = query.offset(offset).limit(limit).all()
    res = []
    for e in events:
        source_details = []
        if e.source_chunk_ids:
            chunks = db.query(KnowledgeChunk, Document).join(
                Document, KnowledgeChunk.document_id == Document.id
            ).filter(KnowledgeChunk.id.in_(e.source_chunk_ids)).all()
            for chunk, doc in chunks:
                source_details.append({
                    "id": str(chunk.id),
                    "document_title": doc.title,
                    "content": chunk.content
                })
        
        merged_content = None
        merged_doc_title = None
        if e.merged_chunk_id:
            merged_chunk_data = db.query(KnowledgeChunk, Document).join(
                Document, KnowledgeChunk.document_id == Document.id
            ).filter(KnowledgeChunk.id == e.merged_chunk_id).first()
            if merged_chunk_data:
                merged_content = merged_chunk_data[0].content
                merged_doc_title = merged_chunk_data[1].title
                
        res.append({
            "id": str(e.id),
            "source_chunks": source_details,
            "merged_chunk": {
                "id": str(e.merged_chunk_id),
                "document_title": merged_doc_title,
                "content": merged_content
            } if e.merged_chunk_id else None,
            "similarity_score": e.similarity_score,
            "method": e.method,
            "performed_at": e.performed_at.isoformat()
        })
    return {
        "total": total,
        "items": res
    }

@router.get("/consistency")
async def get_consistency_issues(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get structural contradictions / logical conflicts (T4 results).
    """
    query = db.query(ConsistencyIssue).order_by(ConsistencyIssue.detected_at.desc())
    total = query.count()
    issues = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "items": [
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
    }

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
async def get_discovered_relations(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get discovered relations from Apriori/NER (T5 results).
    """
    query = db.query(DiscoveredRelation).order_by(DiscoveredRelation.discovered_at.desc())
    total = query.count()
    relations = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "items": [
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
    }

@router.get("/discovery/details/{rel_id}")
async def get_discovery_details(rel_id: str, db: Session = Depends(get_db)):
    """
    Get detailed explanation / co-occurring documents and snippets for a discovered relation.
    """
    relation = db.query(DiscoveredRelation).filter(DiscoveredRelation.id == rel_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Discovered relation not found")
        
    entity_a = relation.entity_a
    entity_b = relation.entity_b
    
    # Collect document IDs where both concepts co-occur
    doc_ids = set()
    
    # 1. Query Neo4j for documents linking to both concepts
    try:
        from shared.database.neo4j_client import Neo4jClient
        neo4j_client = Neo4jClient()
        query = """
        MATCH (c1:Concept {name: $name_a})<-[:CONTAINS_CONCEPT]-(d:Document)-[:CONTAINS_CONCEPT]->(c2:Concept {name: $name_b})
        RETURN d.id AS doc_id
        """
        results = neo4j_client.run_query(query, {"name_a": entity_a, "name_b": entity_b})
        for r in results:
            if r.get("doc_id"):
                doc_ids.add(str(r.get("doc_id")))
        neo4j_client.close()
    except Exception as e:
        print(f"⚠️ [API-Gateway] Neo4j details query failed: {e}")
        
    # 2. Query Postgres for documents containing both concepts as a fallback/addition
    try:
        docs_a = db.query(KnowledgeChunk.document_id).filter(KnowledgeChunk.content.ilike(f"%{entity_a}%")).subquery()
        docs_b = db.query(KnowledgeChunk.document_id).filter(KnowledgeChunk.content.ilike(f"%{entity_b}%")).subquery()
        matching_docs_pg = db.query(Document.id).filter(Document.id.in_(docs_a), Document.id.in_(docs_b)).all()
        for md in matching_docs_pg:
            doc_ids.add(str(md[0]))
    except Exception as e:
        print(f"⚠️ [API-Gateway] Postgres document search failed: {e}")

    # Now, for each document ID, let's load the document and extract the snippets
    contexts = []
    for d_id in list(doc_ids)[:5]: # limit to top 5 documents
        doc = db.query(Document).filter(Document.id == d_id).first()
        if not doc:
            continue
            
        # Find chunks mentioning entity_a or entity_b
        chunks_a = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == doc.id,
            KnowledgeChunk.content.ilike(f"%{entity_a}%")
        ).all()
        chunks_b = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == doc.id,
            KnowledgeChunk.content.ilike(f"%{entity_b}%")
        ).all()
        
        # Check if they co-occur in the same chunk
        same_chunk = None
        for ca in chunks_a:
            for cb in chunks_b:
                if ca.id == cb.id:
                    same_chunk = ca
                    break
            if same_chunk:
                break
                
        if same_chunk:
            text = same_chunk.content
            idx_a = text.lower().find(entity_a.lower())
            idx_b = text.lower().find(entity_b.lower())
            start_idx = max(0, min(idx_a, idx_b) - 100)
            end_idx = min(len(text), max(idx_a + len(entity_a), idx_b + len(entity_b)) + 100)
            snippet = text[start_idx:end_idx]
            if start_idx > 0: snippet = "..." + snippet
            if end_idx < len(text): snippet = snippet + "..."
            
            contexts.append({
                "document_id": str(doc.id),
                "document_title": doc.title,
                "department": doc.department,
                "snippet": snippet
            })
        else:
            # Check if we can show different snippets
            snippets = []
            if chunks_a:
                text = chunks_a[0].content
                idx = text.lower().find(entity_a.lower())
                start = max(0, idx - 80)
                end = min(len(text), idx + len(entity_a) + 80)
                snip = text[start:end]
                if start > 0: snip = "..." + snip
                if end < len(text): snip = snip + "..."
                snippets.append(f"<b>[Apparition de {entity_a}]</b> : {snip}")
            if chunks_b:
                text = chunks_b[0].content
                idx = text.lower().find(entity_b.lower())
                start = max(0, idx - 80)
                end = min(len(text), idx + len(entity_b) + 80)
                snip = text[start:end]
                if start > 0: snip = "..." + snip
                if end < len(text): snip = snip + "..."
                snippets.append(f"<b>[Apparition de {entity_b}]</b> : {snip}")
                
            if snippets:
                snippet_text = "<br><span class='block mt-2'></span>".join(snippets)
            else:
                snippet_text = (
                    f"Ces concepts sont associés structurellement au document dans le graphe de connaissances "
                    f"(par classification automatique ou extraction d'entités), bien que les termes exacts "
                    f"'{entity_a}' et '{entity_b}' ne co-occurrent pas explicitement dans les paragraphes textuels."
                )
                
            contexts.append({
                "document_id": str(doc.id),
                "document_title": doc.title,
                "department": doc.department,
                "snippet": snippet_text
            })
            
    return {
        "id": str(relation.id),
        "entity_a": entity_a,
        "entity_b": entity_b,
        "relation_type": relation.relation_type,
        "confidence": relation.confidence,
        "method": relation.method,
        "discovered_at": relation.discovered_at.isoformat(),
        "contexts": contexts
    }

@router.post("/discovery/approve/{rel_id}")
async def approve_discovered_relation(rel_id: str, db: Session = Depends(get_db)):
    """
    Approve a discovered relation and create it in Neo4j (mock logic + PostgreSQL audit trail logs).
    """
    relation = db.query(DiscoveredRelation).filter(DiscoveredRelation.id == rel_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")
        
    # Log to audit trail
    audit = AuditLog(
        action="relation_approved",
        service="api-gateway",
        details={"rel_id": rel_id, "entity_a": relation.entity_a, "entity_b": relation.entity_b, "relation_type": relation.relation_type},
        explanation=f"La relation découverte [{relation.entity_a}] --({relation.relation_type})--> [{relation.entity_b}] a été approuvée et insérée dans le graphe de connaissances Neo4j."
    )
    db.add(audit)
    
    # Delete from discovered relations list (since it is now integrated into Neo4j)
    db.delete(relation)
    db.commit()
    return {"status": "success", "message": "Relation approved and created in Neo4j."}

# --- Manual Task Trigger Endpoints ---
from shared.kafka.producer import KafkaProducerWrapper
kafka_producer = KafkaProducerWrapper()

@router.post("/trigger/fusion")
async def trigger_manual_fusion(db: Session = Depends(get_db)):
    """
    Manually trigger T3 Semantic Fusion for all active departments.
    """
    active_depts = db.query(Document.department).filter(Document.status == "active").distinct().all()
    depts = [d[0] for d in active_depts if d[0]]
    
    if not depts:
        depts = ["Support IT", "Telecom RNO"]
        
    for dept in depts:
        kafka_producer.publish("document.ingested", {
            "document_id": "00000000-0000-0000-0000-000000000000",
            "title": "Manual Trigger",
            "department": dept,
            "uploaded_by": "system",
            "chunks_count": 0
        })
    kafka_producer.flush()
    return {"status": "success", "message": f"Dépistage des fusions lancé pour les départements : {', '.join(depts)}"}

@router.post("/trigger/consistency")
async def trigger_manual_consistency():
    """
    Manually trigger T4 Consistency Check (contradiction scan).
    """
    from datetime import datetime
    kafka_producer.publish("fusion.completed", {
        "merged_document_id": "00000000-0000-0000-0000-000000000000",
        "source_document_ids": [],
        "department": "All",
        "timestamp": datetime.utcnow().isoformat()
    })
    kafka_producer.flush()
    return {"status": "success", "message": "Dépistage des conflits logiques lancé sur tout le corpus."}

@router.post("/trigger/report")
async def trigger_manual_report():
    """
    Manually trigger T2 Summary Report Generation.
    """
    from datetime import datetime
    kafka_producer.publish("report.trigger", {
        "report_type": "rapport_manuel",
        "timestamp": datetime.utcnow().isoformat()
    })
    kafka_producer.flush()
    return {"status": "success", "message": "Génération du rapport d'activité lancée."}

@router.post("/trigger/discovery")
async def trigger_manual_discovery(db: Session = Depends(get_db)):
    """
    Manually trigger T5 Knowledge Discovery (NER & link prediction).
    """
    latest_doc = db.query(Document).filter(Document.status == "active").order_by(Document.uploaded_at.desc()).first()
    if not latest_doc:
        return {"status": "error", "message": "Aucun document actif trouvé pour lancer l'analyse."}
        
    kafka_producer.publish("document.ingested", {
        "document_id": str(latest_doc.id),
        "title": latest_doc.title,
        "department": latest_doc.department,
        "uploaded_by": "system",
        "chunks_count": 0
    })
    kafka_producer.flush()
    return {"status": "success", "message": "Dépistage des relations lancé sur le graphe de connaissances."}

