import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from shared.kafka.consumer import KafkaConsumerBase
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.postgres import SessionLocal, Document, UpdateReport, AuditLog
import httpx

# Configure GitHub Models client
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")

class T2ReportConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__(
            "t2-report-group", 
            ["prediction.scored", "fusion.completed", "consistency.checked", "discovery.found", "report.trigger"]
        )
        self.producer = KafkaProducerWrapper()

def call_github_model_api(prompt: str) -> str:
    """Helper to call GitHub Models API with error handling and fallback."""
    try:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                { "role": "system", "content": "You are a helpful assistant." },
                { "role": "user", "content": prompt }
            ],
            "model": GITHUB_MODEL,
            "temperature": 0.2
        }
        with httpx.Client() as httpx_client:
            response = httpx_client.post(
                "https://models.github.ai/inference/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ GitHub Models API execution failed: {e}. Falling back to rule-based generation.")
    
    return generate_fallback_report(prompt)

def generate_fallback_report(prompt: str) -> str:
    """Generates a structured mock French report when GitHub Models API is unavailable or fails."""
    return f"""# 📊 Rapport d'activité EvoKnow (Génération locale)

*Date de génération : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*

> **Avis** : Ce rapport a été généré via le système de repli local en raison de l'absence ou de l'échec de la connexion à l'API GitHub Models.

## 📝 Résumé de l'analyse
Le pipeline EvoKnow a traité les événements du cycle de vie des connaissances.

## 🔍 Éléments clés identifiés
1. **Surveillance d'obsolescence (T1)** : Plusieurs documents ont été évalués. Le système a calculé des scores de dégradation basés sur l'âge et la baisse de fréquentation.
2. **Fusion sémantique (T3)** : Consolidation des doublons textuels pour réduire la redondance.
3. **Analyse de cohérence (T4)** : Détection automatique des contradictions conceptuelles.
4. **Découverte de connaissances (T5)** : Extraction d'entités nommées et suggestion de nouvelles relations sémantiques.

*Veuillez vous assurer que l'accès à l'API GitHub Models et le modèle `{GITHUB_MODEL}` sont configurés correctement pour obtenir des analyses générées par l'IA.*
"""

def generate_report(report_type: str, context_data: dict, db: Session) -> str:
    """Builds prompt and calls GitHub Models API to generate a tailored report in French."""
    prompt = f"""Vous êtes un assistant IA spécialisé en gestion des connaissances (Knowledge Management - KM) pour EvoKnow.
Générez un rapport professionnel structuré en Markdown, rédigé EXCLUSIVEMENT en français.

Type de rapport demandé : {report_type}

Données de contexte système :
{json.dumps(context_data, indent=2, ensure_ascii=False)}

Instructions de structure :
1. Titre principal clair et professionnel.
2. Synthèse managériale (2-3 phrases).
3. Section détaillée sur l'activité observée.
4. Tableau récapitulatif (si applicable).
5. Recommandations concrètes pour les gestionnaires de connaissances.

Rédigez un rapport complet, sans raccourcis de type "insérez ici". Soyez précis et professionnel.
"""
    return call_github_model_api(prompt)

def handle_message(topic, payload):
    print(f"📊 [T2-Report] Received event from {topic}: {payload}")
    db = SessionLocal()
    try:
        report_type = None
        context_data = {"event_source": topic, "payload": payload}
        trigger_generation = False
        
        if topic == "prediction.scored":
            score = payload.get("score", 0.0)
            if score >= 0.7:
                report_type = "alert_report"
                doc_id = payload.get("document_id")
                doc = db.query(Document).filter(Document.id == doc_id).first()
                context_data["document"] = {
                    "id": doc_id,
                    "title": doc.title if doc else "Inconnu",
                    "department": doc.department if doc else "Inconnu",
                    "uploaded_by": doc.uploaded_by if doc else "Inconnu"
                }
                context_data["score"] = score
                context_data["factors"] = payload.get("factors", {})
                trigger_generation = True
                print(f"📊 [T2-Report] High obsolescence score ({score}) detected. Triggering alert report.")
                
        elif topic == "fusion.completed":
            report_type = "fusion_report"
            trigger_generation = True
            print(f"📊 [T2-Report] Fusion completed. Triggering fusion report.")
            
        elif topic == "consistency.checked":
            report_type = "consistency_report"
            trigger_generation = True
            print(f"📊 [T2-Report] Consistency checked. Triggering consistency report.")
            
        elif topic == "discovery.found":
            report_type = "discovery_report"
            trigger_generation = True
            print(f"📊 [T2-Report] Knowledge discovery event. Triggering discovery report.")
            
        elif topic == "report.trigger":
            report_type = payload.get("report_type", "weekly_summary")
            trigger_generation = True
            
            if report_type == "weekly_summary":
                total_docs = db.query(Document).filter(Document.status == "active").count()
                archived_docs = db.query(Document).filter(Document.status == "archived").count()
                context_data["system_stats"] = {
                    "total_active_documents": total_docs,
                    "total_archived_documents": archived_docs,
                    "timestamp": datetime.utcnow().isoformat()
                }
            print(f"📊 [T2-Report] Manual or scheduled report trigger received for type: {report_type}.")

        if trigger_generation and report_type:
            print(f"📊 [T2-Report] Generating {report_type}...")
            report_content = generate_report(report_type, context_data, db)
            
            report_entry = UpdateReport(
                report_type=report_type,
                content_md=report_content
            )
            db.add(report_entry)
            db.commit()
            db.refresh(report_entry)
            
            audit = AuditLog(
                action="GENERATE_REPORT",
                service="t2-report-generation",
                details={
                    "report_id": str(report_entry.id),
                    "report_type": report_type
                },
                explanation=f"Rapport de type '{report_type}' généré avec succès par l'IA et enregistré dans la base de données."
            )
            db.add(audit)
            db.commit()
            
            producer = KafkaProducerWrapper()
            producer.publish("report.generated", {
                "report_id": str(report_entry.id),
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat()
            })
            producer.flush()
            print(f"📊 [T2-Report] Report {report_entry.id} of type {report_type} published successfully.")
            
    except Exception as e:
        print(f"⚠️ [T2-Report] Error in message handler: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting T2 Report Generation Service...")
    consumer = T2ReportConsumer()
    consumer.consume(handle_message)
