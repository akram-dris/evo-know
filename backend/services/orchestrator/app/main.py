import os
import json
from datetime import datetime
from shared.kafka.consumer import KafkaConsumerBase
from shared.database.postgres import SessionLocal, AuditLog

class OrchestratorConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__(
            "orchestrator-group", 
            [
                "document.ingested",
                "discovery.found",
                "fusion.completed",
                "consistency.checked",
                "prediction.scored",
                "report.generated"
            ]
        )

def log_orchestration_step(topic: str, payload: dict):
    db = SessionLocal()
    try:
        doc_id = payload.get("document_id") or payload.get("merged_document_id")
        timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
        
        details = {
            "kafka_topic": topic,
            "payload": payload,
            "timestamp": timestamp
        }
        
        explanation = ""
        action = f"ORCHESTRATE_{topic.upper().replace('.', '_')}"
        
        if topic == "document.ingested":
            title = payload.get("title", "Document")
            explanation = (
                f"Déclenchement du pipeline d'ingestion. Nouveau document reçu : '{title}' "
                f"pour le département '{payload.get('department')}'. Lancement de la découpe sémantique "
                f"et de la mise à indexation FAISS."
            )
        elif topic == "discovery.found":
            explanation = (
                f"Étape Découverte (T5) validée. {payload.get('concepts_extracted_count')} concepts "
                f"extraits et {payload.get('new_relations_discovered_count')} relations découvertes "
                f"ont été intégrés dans le graphe de connaissances Neo4j."
            )
        elif topic == "fusion.completed":
            explanation = (
                f"Étape Fusion Sémantique (T3) complétée. Les anciens documents ont été archivés "
                f"et redirigés vers le nouveau document fusionné (ID: {doc_id})."
            )
        elif topic == "consistency.checked":
            explanation = (
                f"Étape Vérification de Cohérence (T4) validée. Le système a trouvé "
                f"{payload.get('textual_issues_count')} contradictions textuelles et "
                f"{payload.get('graph_issues_count')} anomalies structurelles dans Neo4j."
            )
        elif topic == "prediction.scored":
            explanation = (
                f"Étape Score d'Obsolescence (T1) validée. Le score calculé pour le document "
                f"est de {payload.get('score')}. Diagnostic basé sur les courbes d'accès et l'âge."
            )
        elif topic == "report.generated":
            explanation = (
                f"Étape finale : Rapport généré (T2). Le rapport de mise à jour sémantique "
                f"de type '{payload.get('report_type')}' est disponible dans le registre pour consultation."
            )
            
        audit = AuditLog(
            action=action,
            service="orchestrator",
            details=details,
            explanation=explanation
        )
        db.add(audit)
        db.commit()
        print(f"⚡ [Orchestrator] Step logged: {action} - {explanation}")
        
    except Exception as e:
        print(f"⚠️ [Orchestrator] Error logging step: {e}")
        db.rollback()
    finally:
        db.close()

def handle_message(topic, payload):
    print(f"⚡ [Orchestrator] Processing event from {topic}: {payload}")
    log_orchestration_step(topic, payload)

if __name__ == "__main__":
    print("🚀 Starting AI Orchestrator Daemon...")
    consumer = OrchestratorConsumer()
    consumer.consume(handle_message)
