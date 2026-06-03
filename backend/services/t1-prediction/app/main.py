import os
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from shared.kafka.consumer import KafkaConsumerBase
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.postgres import SessionLocal, Document, KnowledgeChunk, ObsolescenceScore, AuditLog, AccessLog
from shared.database.vector_store import VectorStore
from shared.embeddings.encoder import KnowledgeEncoder

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not available. Falling back to statistical trend models.")

class T1PredictionConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t1-prediction-group", ["document.ingested", "access.logged"])
        self.producer = KafkaProducerWrapper()
        self.vector_store = VectorStore()
        self.encoder = KnowledgeEncoder()

def calculate_obsolescence(doc_id: str, db: Session, vector_store: VectorStore) -> dict:
    doc = db.query(Document).filter(Document.id == doc_id, Document.status == "active").first()
    if not doc:
        return {}

    now = datetime.utcnow()
    age_days = (now - doc.uploaded_at).days
    days_since_update = (now - doc.last_updated).days
    
    age_factor = min(1.0, max(0.0, age_days / 365.0))
    update_factor = min(1.0, max(0.0, days_since_update / 180.0))
    combined_age_score = 0.4 * age_factor + 0.6 * update_factor

    cutoff_90d = now - timedelta(days=90)
    logs = db.query(AccessLog).filter(
        AccessLog.document_id == doc_id,
        AccessLog.accessed_at >= cutoff_90d
    ).all()

    access_trend_score = 0.5
    
    if len(logs) > 0:
        log_dates = [log.accessed_at.date() for log in logs]
        date_range = pd.date_range(end=now.date(), periods=90, freq='D')
        ts_df = pd.DataFrame(index=date_range)
        ts_df['access_count'] = 0
        
        for d in log_dates:
            if d in ts_df.index:
                ts_df.loc[d, 'access_count'] += 1

        count_7d = ts_df.iloc[-7:]['access_count'].sum()
        count_30d = ts_df.iloc[-30:]['access_count'].sum()
        
        if count_30d == 0:
            access_trend_score = 0.8
        else:
            if PROPHET_AVAILABLE and len(logs) >= 15:
                try:
                    prophet_df = ts_df.reset_index().rename(columns={'index': 'ds', 'access_count': 'y'})
                    model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
                    model.fit(prophet_df)
                    
                    future = model.make_future_dataframe(periods=30)
                    forecast = model.predict(future)
                    
                    predicted_mean = forecast['yhat'].iloc[-30:].mean()
                    current_mean = ts_df['access_count'].iloc[-30:].mean()
                    
                    if current_mean == 0:
                        access_trend_score = 0.8
                    else:
                        decline = (current_mean - predicted_mean) / current_mean
                        access_trend_score = min(1.0, max(0.0, decline))
                except Exception as e:
                    print(f"Prophet fitting failed: {e}. Falling back to statistical trend.")
                    weekly_avg = count_30d / 4.28
                    decline = (weekly_avg - count_7d) / max(1.0, weekly_avg)
                    access_trend_score = min(1.0, max(0.0, decline))
            else:
                weekly_avg = count_30d / 4.28
                decline = (weekly_avg - count_7d) / max(1.0, weekly_avg)
                access_trend_score = min(1.0, max(0.0, decline))

    superseded_score = 0.0
    doc_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc_id).all()
    
    if doc_chunks and vector_store.index.ntotal > 0:
        max_sim = 0.0
        for chunk in doc_chunks:
            if chunk.embedding:
                arr = np.frombuffer(chunk.embedding, dtype=np.float32)
                matches = vector_store.search(arr, top_k=10)
                for match in matches:
                    if match['id'] == str(chunk.id):
                        continue
                    matched_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == match['id']).first()
                    if matched_chunk:
                        matched_doc = db.query(Document).filter(
                            Document.id == matched_chunk.document_id,
                            Document.status == "active",
                            Document.uploaded_at > doc.uploaded_at,
                            Document.department == doc.department
                        ).first()
                        if matched_doc:
                            if match['score'] > max_sim:
                                max_sim = match['score']
        
        if max_sim > 0.85:
            superseded_score = min(1.0, (max_sim - 0.8) * 5.0)

    final_score = (0.3 * combined_age_score) + (0.4 * access_trend_score) + (0.3 * superseded_score)
    final_score = round(min(1.0, max(0.0, final_score)), 3)

    factors = {
        "combined_age_score": round(combined_age_score, 3),
        "access_trend_score": round(access_trend_score, 3),
        "superseded_score": round(superseded_score, 3),
        "age_days": age_days,
        "days_since_update": days_since_update,
        "logs_analyzed": len(logs)
    }
    
    return {
        "document_id": doc_id,
        "score": final_score,
        "factors": factors
    }

def handle_message(topic, payload):
    print(f"🧠 [T1-Prediction] Received event from {topic}: {payload}")
    db = SessionLocal()
    try:
        doc_ids_to_evaluate = []
        
        if topic == "document.ingested":
            dept = payload.get("department")
            if dept:
                docs = db.query(Document).filter(
                    Document.department == dept,
                    Document.status == "active"
                ).all()
                doc_ids_to_evaluate = [str(d.id) for d in docs]
            else:
                doc_ids_to_evaluate = [payload.get("document_id")]
        elif topic == "access.logged":
            doc_ids_to_evaluate = [payload.get("document_id")]

        doc_ids_to_evaluate = [d for d in doc_ids_to_evaluate if d]
        
        vector_store = VectorStore()

        for doc_id in doc_ids_to_evaluate:
            print(f"🧠 [T1-Prediction] Scoring document: {doc_id}")
            eval_res = calculate_obsolescence(doc_id, db, vector_store)
            if not eval_res:
                continue
                
            score_val = eval_res["score"]
            factors = eval_res["factors"]
            
            score_entry = ObsolescenceScore(
                document_id=uuid.UUID(doc_id),
                score=score_val,
                model_version="Prophet-Hybrid-v1",
                factors=factors
            )
            db.add(score_entry)
            db.commit()
            
            doc = db.query(Document).filter(Document.id == doc_id).first()
            doc_title = doc.title if doc else "Document"
            explanation = (
                f"Le score d'obsolescence pour '{doc_title}' a été calculé à {score_val}. "
                f"Facteurs: Âge et mise à jour = {factors['combined_age_score']}, Trend d'accès = {factors['access_trend_score']}, "
                f"Sémantique de substitution = {factors['superseded_score']}."
            )
            
            audit = AuditLog(
                action="CALCULATE_OBSOLESCENCE",
                service="t1-prediction",
                details={
                    "document_id": doc_id,
                    "score": score_val,
                    "factors": factors
                },
                explanation=explanation
            )
            db.add(audit)
            db.commit()
            
            event_payload = {
                "document_id": doc_id,
                "score": score_val,
                "factors": factors,
                "timestamp": datetime.utcnow().isoformat()
            }
            producer = KafkaProducerWrapper()
            producer.publish("prediction.scored", event_payload)
            producer.flush()
            print(f"🧠 [T1-Prediction] Scored document {doc_id} with score {score_val} and published event.")
            
    except Exception as e:
        print(f"⚠️ [T1-Prediction] Error in message handler: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting T1 Prediction Service...")
    consumer = T1PredictionConsumer()
    consumer.consume(handle_message)
