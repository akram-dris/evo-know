import os
import json
import uuid
from datetime import datetime
from shared.kafka.consumer import KafkaConsumerBase
from shared.database.postgres import SessionLocal, AuditLog
from shared.kafka.producer import KafkaProducer # Import KafkaProducer

producer = KafkaProducer() # Initialize Kafka Producer globally

# Placeholder functions for external interactions (in a real system, these would interact with other services)
def archive_chunk(chunk_id: str):
    print(f"ACTION: Archiving chunk {chunk_id}")

def raise_dashboard_alert(alert_details: dict):
    print(f"ACTION: Publishing dashboard alert to Kafka: {json.dumps(alert_details, indent=2)}")
    producer.produce("orchestrator.alert", alert_details)

class KMOrchestrator:
    """
    Coordinates T1-T5, manages scheduler loop, handles conflict resolution,
    and writes XAI explanations to the postgres audit database.
    """
    def __init__(self):
        self.db = SessionLocal()

    def _log_xai_audit(self, action: str, explanation: str, service: str, details: dict = None):
        try:
            audit = AuditLog(
                action=action,
                service=service,
                details=details,
                explanation=explanation
            )
            self.db.add(audit)
            self.db.commit()
            print(f"⚡ [Orchestrator] Audit logged: {action} - {explanation}")
        except Exception as e:
            print(f"⚠️ [Orchestrator] Error logging audit: {e}")
            self.db.rollback()

    def resolve_conflicts(self, conflict: dict):
        """
        Resolves conflicts detected in the knowledge base, potentially by
        auto-superseding older content or raising alerts.
        """
        if conflict.get("age_diff_days", 0) > 180:
            # Auto-supersede older chunk
            older_chunk_id = conflict.get("older_chunk_id")
            newer_chunk_id = conflict.get("newer_chunk_id")
            archive_chunk(older_chunk_id)
            explanation = (
                f"Contenu obsolète auto-remplacé. Le fragment ancien '{older_chunk_id}' "
                f"a été archivé en faveur du nouveau '{newer_chunk_id}' (différence d'âge : "
                f"{conflict['age_diff_days']} jours). Le système a pris une décision autonome "
                f"en se basant sur des règles d'ancienneté préétablies pour maintenir la "
                f"pertinence de la base de connaissances."
            )
            self._log_xai_audit(
                action="auto_supersede",
                explanation=explanation,
                service="orchestrator",
                details=conflict
            )
        else:
            # Escalate to Vue frontend dashboard as an active alert
            alert_id = str(uuid.uuid4())
            alert_details = {
                "id": alert_id,
                "title": "Conflit de connaissances détecté",
                "message": (
                    f"Un conflit potentiel entre des fragments de connaissances a été détecté. "
                    f"Veuillez examiner les fragments suivants pour une résolution manuelle. "
                    f"Détails : {conflict.get('description', 'Non spécifié')}."
                ),
                "severity": "critical",
                "conflict_data": conflict,
                "timestamp": datetime.utcnow().isoformat()
            }
            raise_dashboard_alert(alert_details)
            explanation = (
                f"Conflit de connaissances remonté. Le conflit nécessite une intervention humaine "
                f"en raison de critères non remplis pour la résolution automatique (différence "
                f"d'âge de {conflict.get('age_diff_days', 0)} jours inférieure au seuil)."
            )
            self._log_xai_audit(
                action="conflict_escalated",
                explanation=explanation,
                service="orchestrator",
                details=alert_details
            )

    def process_event(self, topic: str, payload: dict):
        """Processes an incoming Kafka event and orchestrates actions."""
        print(f"⚡ [Orchestrator] Processing event from {topic}: {payload}")
        
        # Example orchestration logic (simplified)
        if topic == "consistency.checked":
            # Assuming payload contains details about conflicts
            if payload.get("conflicts_found"):
                for conflict in payload["conflicts_found"]:
                    self.resolve_conflicts(conflict)
            explanation = (
                f"Étape Vérification de Cohérence (T4) terminée. "
                f"{payload.get('textual_issues_count', 0)} contradictions textuelles et "
                f"{payload.get('graph_issues_count', 0)} anomalies structurelles traitées. "
                f"{payload.get('conflicts_found_count', 0)} conflits potentiels trouvés."
            )
            self._log_xai_audit(
                action="consistency_checked_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
        elif topic == "fusion.completed":
            explanation = (
                f"Étape Fusion Sémantique (T3) terminée. "
                f"Fragments fusionnés : {payload.get('merged_chunk_id')}. "
                f"L'orchestrateur a validé l'opération de fusion et déclenche potentiellement "
                f"une vérification de cohérence."
            )
            self._log_xai_audit(
                action="fusion_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
        elif topic == "document.ingested":
            title = payload.get("title", "Document")
            explanation = (
                f"Nouveau document '{title}' ingéré pour '{payload.get('department')}'. "
                f"L'orchestrateur déclenche les processus d'extraction, d'intégration "
                f"et de scoring initiaux."
            )
            self._log_xai_audit(
                action="document_ingestion_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
        elif topic == "prediction.scored":
            score = payload.get("score")
            explanation = (
                f"Score d'obsolescence (T1) calculé pour le document {payload.get('document_id')}: {score}. "
                f"Si le score est élevé ({score}), l'orchestrateur peut déclencher des alertes ou des actions de vérification."
            )
            self._log_xai_audit(
                action="prediction_scored_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
            if score > 0.7: # Example threshold for high obsolescence
                alert_id = str(uuid.uuid4())
                alert_details = {
                    "id": alert_id,
                    "title": "Document potentiellement obsolète",
                    "message": (
                        f"Le document '{payload.get('document_id')}' présente un score d'obsolescence élevé ({score}). "
                        f"Il est recommandé de vérifier sa pertinence."
                    ),
                    "severity": "warning",
                    "document_id": payload.get("document_id"),
                    "score": score,
                    "timestamp": datetime.utcnow().isoformat()
                }
                raise_dashboard_alert(alert_details)
                self._log_xai_audit(
                    action="obsolescence_alert_raised",
                    explanation=f"Alerte d'obsolescence élevée ({score}) pour le document {payload.get('document_id')} transmise au tableau de bord.",
                    service="orchestrator",
                    details=alert_details
                )
        elif topic == "report.generated":
            explanation = (
                f"Rapport de mise à jour (T2) généré: '{payload.get('report_type')}' pour {payload.get('generated_at')}. "
                f"L'orchestrateur confirme la génération du rapport et sa disponibilité."
            )
            self._log_xai_audit(
                action="report_generation_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
        elif topic == "discovery.found":
            explanation = (
                f"Nouvelles connaissances découvertes (T5). "
                f"{payload.get('new_relations_count', 0)} relations ont été identifiées. "
                f"L'orchestrateur intègre ces découvertes et peut déclencher des vérifications."
            )
            self._log_xai_audit(
                action="discovery_orchestrated",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )
        else:
            explanation = f"Événement inconnu reçu par l'orchestrateur: {topic}."
            self._log_xai_audit(
                action="unknown_event",
                explanation=explanation,
                service="orchestrator",
                details=payload
            )

    def __del__(self):
        self.db.close()


class OrchestratorConsumer(KafkaConsumerBase):
    def __init__(self, orchestrator: KMOrchestrator):
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
        self.orchestrator = orchestrator

    def handle_message(self, topic, payload):
        self.orchestrator.process_event(topic, payload)


if __name__ == "__main__":
    print("🚀 Starting AI Orchestrator Daemon...")
    orchestrator_instance = KMOrchestrator()
    consumer = OrchestratorConsumer(orchestrator_instance)
    consumer.consume(consumer.handle_message)

