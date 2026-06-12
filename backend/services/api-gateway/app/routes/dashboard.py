from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from shared.database.postgres import (
    get_db, Document, UpdateReport, FusionEvent, 
    ConsistencyIssue, DiscoveredRelation, AuditLog, ObsolescenceScore
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

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
            
        recent_alerts_payload.append({
            "id": str(a.id),
            "title": a.action.replace("_", " ").title(),
            "desc": a.explanation,
            "time": time_str,
            "severity": severity,
            "bgClass": bg
        })
        
    # If no database alerts exist, fallback to static template alerts
    if not recent_alerts_payload:
        recent_alerts_payload = [
            { 
                "id": "1", 
                "title": "Obsolescence imminente (Seed)", 
                "desc": "Accès au document 'OSS-4G-Procedure-v2' en baisse de 82% sur 30 jours.", 
                "time": "Il y a 12 min", 
                "severity": "high", 
                "bgClass": "bg-rose-500/5 border-rose-100 border-l-rose-500" 
            }
        ]

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
