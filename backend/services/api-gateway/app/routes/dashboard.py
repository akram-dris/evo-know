from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from shared.database.postgres import (
    get_db, Document, UpdateReport, FusionEvent, 
    ConsistencyIssue, DiscoveredRelation, AuditLog, ObsolescenceScore,
    KnowledgeChunk
)
from shared.kafka.producer import KafkaProducerWrapper

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
kafka_producer = KafkaProducerWrapper()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Exposes aggregate counts and lists for the dashboard.
    """
    # 1. T1 Obsolescence count (docs with score > 0.7)
    t1_count = db.query(ObsolescenceScore).filter(ObsolescenceScore.score > 0.7).count()
    
    # 2. T2 Reports count
    t2_count = db.query(UpdateReport).count()
    
    # 3. T3 Fusions count
    t3_count = db.query(FusionEvent).count()
    
    # 4. T4 Consistency index calculation
    t4_unresolved = db.query(ConsistencyIssue).filter(ConsistencyIssue.resolved == False).count()
    t4_index = max(0.0, 100.0 - (t4_unresolved * 3.6))
    
    # 5. T5 Discovered relations count
    t5_count = db.query(DiscoveredRelation).count()
    
    # Recent alerts from AuditLog
    alerts = db.query(AuditLog).filter(
        AuditLog.action.in_(["obsolescence_alert_raised", "conflict_escalated", "unknown_event"])
    ).order_by(AuditLog.performed_at.desc()).limit(3).all()
    
    action_translations = {
        "auto_supersede": "Remplacement automatique",
        "conflict_escalated": "Conflit logique détecté",
        "consistency_checked_orchestrated": "Vérification de cohérence",
        "fusion_orchestrated": "Validation de fusion sémantique",
        "document_ingestion_orchestrated": "Ingestion de document",
        "prediction_scored_orchestrated": "Scoring d'obsolescence",
        "obsolescence_alert_raised": "Alerte d'obsolescence émise",
        "report_generation_orchestrated": "Génération de rapport",
        "discovery_orchestrated": "Découverte de connaissances",
        "unknown_event": "Événement inconnu",
        "conflict_resolved_manually": "Conflit résolu manuellement",
        "relation_approved": "Relation approuvée",
        "manual_pipeline_scan_triggered": "Scan manuel du pipeline"
    }

    recent_alerts_payload = []
    for a in alerts:
        severity = "critical" if a.action == "conflict_escalated" else "warning"
        bg = "bg-rose-500/5 border-rose-100 border-l-rose-500" if severity == "critical" else "bg-amber-500/5 border-amber-100 border-l-amber-500"
        
        # Calculate time elapsed
        diff = datetime.now(timezone.utc) - a.performed_at
        if diff.seconds < 60:
            time_str = "Il y a quelques instants"
        elif diff.seconds < 3600:
            time_str = f"Il y a {diff.seconds // 60} min"
        else:
            time_str = f"Il y a {diff.seconds // 3600} heures"
            
        display_title = action_translations.get(a.action, a.action.replace("_", " ").title())
        recent_alerts_payload.append({
            "id": str(a.id),
            "title": display_title,
            "desc": a.explanation,
            "time": time_str,
            "severity": severity,
            "bgClass": bg
        })
        


    # Recent activities (logs)
    activities = db.query(AuditLog).order_by(AuditLog.performed_at.desc()).limit(5).all()
    recent_activities_payload = []
    for act in activities:
        badge_type = "Activité"
        color = "bg-blue-50 text-blue-700 border-blue-200/50"
        
        if "ingest" in act.action:
            badge_type = "Ingestion"
            color = "bg-indigo-50 text-indigo-700 border-indigo-200/50"
        elif "fusion" in act.action:
            badge_type = "Fusion"
            color = "bg-emerald-50 text-emerald-700 border-emerald-200/50"
        elif "consistency" in act.action:
            badge_type = "Cohérence"
            color = "bg-rose-50 text-rose-700 border-rose-200/50"
        elif "discovery" in act.action:
            badge_type = "Découverte"
            color = "bg-amber-50 text-amber-700 border-amber-200/50"
            
        diff = datetime.now(timezone.utc) - act.performed_at
        if diff.seconds < 60:
            time_str = "A l'instant"
        elif diff.seconds < 3600:
            time_str = f"Il y a {diff.seconds // 60} min"
        else:
            time_str = f"Il y a {diff.seconds // 3600} h"

        recent_activities_payload.append({
            "id": str(act.id),
            "type": badge_type,
            "message": act.explanation,
            "time": time_str,
            "badgeColor": color
        })

    return {
        "stats": [
            {"name": "T1 : Risque d'obsolescence", "value": f"{t1_count} Docs", "change": "Calculé via LSTM/Prophet"},
            {"name": "T2 : Rapports automatiques", "value": f"{t2_count} Rapports", "change": f"Synthétisé par Llama3"},
            {"name": "T3 : Fusions sémantiques", "value": f"{t3_count} Fusions", "change": "Groupement DBSCAN"},
            {"name": "T4 : Indice de cohérence", "value": f"{t4_index:.1f}%", "change": f"{t4_unresolved} conflits en suspens"},
            {"name": "T5 : Relations extraites", "value": f"{t5_count} Liens", "change": "NER CamemBERT + Apriori"}
        ],
        "recentAlerts": recent_alerts_payload,
        "recentActivity": recent_activities_payload
    }

@router.post("/scan")
async def trigger_pipeline_scan(db: Session = Depends(get_db)):
    """
    Manually triggers the KM pipeline analysis on all existing documents
    by re-publishing 'document.ingested' events to Kafka.
    """
    documents = db.query(Document).filter(Document.status == 'active').all()
    if not documents:
        return {"status": "success", "message": "Aucun document actif trouvé pour le scan."}
        
    for doc in documents:
        # Get chunk count
        chunk_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).count()
        
        # Publish Kafka event
        kafka_producer.publish("document.ingested", {
            "document_id": str(doc.id),
            "title": doc.title,
            "department": doc.department,
            "uploaded_by": doc.uploaded_by or "system",
            "chunks_count": chunk_count
        })
        
    # Also log to audit
    audit = AuditLog(
        action="manual_pipeline_scan_triggered",
        service="api-gateway",
        explanation=f"Scan manuel du pipeline lancé pour {len(documents)} document(s)."
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "message": f"Scan du pipeline démarré pour {len(documents)} document(s)."}
