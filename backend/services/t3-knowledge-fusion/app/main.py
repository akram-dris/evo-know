import os
import json
import uuid
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

from shared.kafka.consumer import KafkaConsumerBase
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.postgres import SessionLocal, Document, KnowledgeChunk, FusionEvent, AuditLog
from shared.database.vector_store import VectorStore
from shared.database.neo4j_client import Neo4jClient
from shared.embeddings.encoder import KnowledgeEncoder
from shared.chunking.splitter import KnowledgeChunkSplitter

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

HAS_GEMINI = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        HAS_GEMINI = True
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API in T3: {e}")

class T3FusionConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t3-fusion-group", ["document.ingested"])
        self.producer = KafkaProducerWrapper()

def call_merger_api(chunks_text: list[str]) -> str:
    """Calls Gemini to merge overlapping texts into a single comprehensive paragraph."""
    if HAS_GEMINI:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            segments = "\n".join([f"--- Segment {i+1} ---\n{text}" for i, text in enumerate(chunks_text)])
            prompt = f"""Vous êtes un système automatisé de fusion de connaissances pour EvoKnow.
Les segments de texte suivants proviennent de documents redondants ou superposés.
Fusionnez-les en un seul texte cohérent, exhaustif et sans répétition. Conservez TOUTES les informations uniques importantes (noms, paramètres, versions, processus).
Rédigez le résultat EXCLUSIVEMENT en français.

{segments}

Renvoyez UNIQUEMENT le texte fusionné final. Pas d'introduction, pas de conclusion, pas de balises explicatives.
"""
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini fusion failed: {e}. Falling back to simple concatenation.")
            
    return "\n\n".join(chunks_text)

def run_department_fusion(dept: str, db: Session, vector_store: VectorStore, encoder: KnowledgeEncoder, splitter: KnowledgeChunkSplitter, neo4j_client: Neo4jClient):
    print(f"🔗 [T3-Fusion] Checking for redundancies in department: {dept}")
    
    docs = db.query(Document).filter(Document.department == dept, Document.status == "active").all()
    if len(docs) < 2:
        return
        
    doc_ids = [d.id for d in docs]
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id.in_(doc_ids),
        KnowledgeChunk.embedding != None
    ).all()
    
    if len(chunks) < 2:
        return

    embeddings = []
    chunk_list = []
    for c in chunks:
        arr = np.frombuffer(c.embedding, dtype=np.float32)
        if len(arr) == 384:
            embeddings.append(arr)
            chunk_list.append(c)

    if len(embeddings) < 2:
        return

    emb_matrix = np.array(embeddings)
    dist_matrix = np.clip(1 - cosine_similarity(emb_matrix), 0, None)
    clustering = DBSCAN(eps=0.15, min_samples=2, metric='precomputed')
    labels = clustering.fit_predict(dist_matrix)
    
    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue
        clusters.setdefault(label, []).append(chunk_list[idx])

    for label, cluster_chunks in clusters.items():
        print(f"🔗 [T3-Fusion] Found duplicate cluster {label} with {len(cluster_chunks)} chunks.")
        
        source_doc_ids = list(set([c.document_id for c in cluster_chunks]))
        if len(source_doc_ids) < 2:
            continue
            
        source_docs = db.query(Document).filter(Document.id.in_(source_doc_ids)).all()
        source_titles = [d.title for d in source_docs]
        
        chunks_text = [c.content for c in cluster_chunks]
        merged_text = call_merger_api(chunks_text)
        
        merged_title = f"Fusion: " + " & ".join(source_titles[:3])
        if len(source_titles) > 3:
            merged_title += f" et {len(source_titles) - 3} autres"
            
        merged_doc = Document(
            title=merged_title,
            source_type="fused",
            source_path=None,
            department=dept,
            uploaded_by="EvoKnow Fusion Service",
            status="active"
        )
        db.add(merged_doc)
        db.commit()
        db.refresh(merged_doc)
        
        new_chunks_text = splitter.split(merged_text)
        new_embeddings = encoder.encode(new_chunks_text)
        
        new_chunk_uuids = []
        new_chunk_records = []
        for idx, text in enumerate(new_chunks_text):
            kc = KnowledgeChunk(
                document_id=merged_doc.id,
                chunk_index=idx,
                content=text,
                token_count=len(text.split()),
                embedding=new_embeddings[idx].tobytes()
            )
            db.add(kc)
            db.commit()
            db.refresh(kc)
            new_chunk_uuids.append(str(kc.id))
            new_chunk_records.append(kc)
            
        vector_store.add(new_embeddings, new_chunk_uuids)
        
        source_chunk_uuids = [c.id for c in cluster_chunks]
        fusion_event = FusionEvent(
            source_chunk_ids=source_chunk_uuids,
            merged_chunk_id=new_chunk_records[0].id if new_chunk_records else None,
            similarity_score=float(1.0 - np.mean(dist_matrix[labels == label][:, labels == label])),
            method="DBSCAN-Gemini"
        )
        db.add(fusion_event)
        db.commit()
        
        for doc in source_docs:
            doc.status = "archived"
            doc.last_updated = datetime.utcnow()
        db.commit()
        
        cypher_query = """
        MERGE (d:Document {id: $merged_doc_id})
        SET d.title = $title, d.department = $dept, d.status = 'active'
        WITH d
        UNWIND $source_doc_ids AS src_id
        MATCH (src:Document {id: src_id})
        SET src.status = 'archived'
        MERGE (src)-[:MERGED_INTO]->(d)
        """
        try:
            neo4j_client.run_query(cypher_query, {
                "merged_doc_id": str(merged_doc.id),
                "title": merged_doc.title,
                "dept": merged_doc.department,
                "source_doc_ids": [str(sid) for sid in source_doc_ids]
            })
        except Exception as e:
            print(f"⚠️ [T3-Fusion] Neo4j graph update failed: {e}")
            
        explanation = (
            f"Fusion sémantique automatique effectuée dans le département '{dept}'. "
            f"Les documents [{', '.join(source_titles)}] ont été fusionnés dans le document principal '{merged_title}' "
            f"pour réduire la redondance textuelle de {len(source_docs)} documents à 1."
        )
        audit = AuditLog(
            action="KNOWLEDGE_FUSION",
            service="t3-knowledge-fusion",
            details={
                "merged_document_id": str(merged_doc.id),
                "source_document_ids": [str(sid) for sid in source_doc_ids],
                "similarity_score": fusion_event.similarity_score
            },
            explanation=explanation
        )
        db.add(audit)
        db.commit()
        
        producer = KafkaProducerWrapper()
        producer.publish("fusion.completed", {
            "merged_document_id": str(merged_doc.id),
            "source_document_ids": [str(sid) for sid in source_doc_ids],
            "department": dept,
            "timestamp": datetime.utcnow().isoformat()
        })
        producer.flush()
        print(f"🔗 [T3-Fusion] Successfully completed fusion event for cluster {label}.")

def handle_message(topic, payload):
    print(f"🔗 [T3-Fusion] Received event from {topic}: {payload}")
    db = SessionLocal()
    neo4j_client = Neo4jClient()
    try:
        dept = payload.get("department")
        if dept:
            vector_store = VectorStore()
            encoder = KnowledgeEncoder()
            splitter = KnowledgeChunkSplitter()
            run_department_fusion(dept, db, vector_store, encoder, splitter, neo4j_client)
            
    except Exception as e:
        print(f"⚠️ [T3-Fusion] Error in message handler: {e}")
        db.rollback()
    finally:
        db.close()
        neo4j_client.close()

if __name__ == "__main__":
    print("🚀 Starting T3 Knowledge Fusion Service...")
    consumer = T3FusionConsumer()
    consumer.consume(handle_message)
