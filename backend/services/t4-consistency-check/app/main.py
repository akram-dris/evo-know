import os
import json
import uuid
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity

from shared.kafka.consumer import KafkaConsumerBase
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.postgres import SessionLocal, Document, KnowledgeChunk, ConsistencyIssue, AuditLog
from shared.database.vector_store import VectorStore
from shared.database.neo4j_client import Neo4jClient

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

HAS_GEMINI = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        HAS_GEMINI = True
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API in T4: {e}")

class T4ConsistencyConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t4-consistency-group", ["document.ingested", "fusion.completed"])
        self.producer = KafkaProducerWrapper()

def call_nli_api(text_a: str, text_b: str) -> dict:
    """Uses Gemini API to run Natural Language Inference (NLI) on two text chunks."""
    if HAS_GEMINI:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = f"""Comparez les deux déclarations suivantes pour déterminer si elles se contredisent logiquement.
Déclaration A : "{text_a}"
Déclaration B : "{text_b}"

Renvoyez le résultat au format JSON brut suivant sans autre texte ou balise Markdown :
{{
  "label": "contradiction" | "neutral" | "entailment",
  "score": 0.0 à 1.0 (degré de confiance),
  "explanation": "Brève explication en français de la contradiction ou de la relation sémantique."
}}
"""
            response = model.generate_content(prompt)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"⚠️ Gemini NLI call failed: {e}. Falling back to default.")
            
    return {"label": "neutral", "score": 1.0, "explanation": "Vérification locale indisponible."}

def run_nli_scan(db: Session, vector_store: VectorStore) -> list[dict]:
    """Scans pairs of similar chunks for logical contradictions."""
    print("⚖️ [T4-Consistency] Running sbert-similar text pairs contradiction scan...")
    active_docs = db.query(Document).filter(Document.status == "active").all()
    active_doc_ids = [d.id for d in active_docs]
    
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id.in_(active_doc_ids),
        KnowledgeChunk.embedding != None
    ).all()
    
    if len(chunks) < 2:
        return []
        
    embeddings = []
    chunk_list = []
    for c in chunks:
        arr = np.frombuffer(c.embedding, dtype=np.float32)
        if len(arr) == 384:
            embeddings.append(arr)
            chunk_list.append(c)
            
    if len(embeddings) < 2:
        return []
        
    emb_matrix = np.array(embeddings)
    sim_matrix = cosine_similarity(emb_matrix)
    
    issues_found = []
    for i in range(len(chunk_list)):
        for j in range(i + 1, len(chunk_list)):
            sim_score = sim_matrix[i][j]
            if sim_score < 0.6:
                continue
                
            chunk_a = chunk_list[i]
            chunk_b = chunk_list[j]
            
            if chunk_a.document_id == chunk_b.document_id:
                continue
                
            nli_res = call_nli_api(chunk_a.content, chunk_b.content)
            
            if nli_res.get("label") == "contradiction" and nli_res.get("score", 0.0) >= 0.7:
                issues_found.append({
                    "chunk_a_id": chunk_a.id,
                    "chunk_b_id": chunk_b.id,
                    "confidence": nli_res["score"],
                    "description": nli_res.get("explanation", "Contradiction sémantique détectée.")
                })
                
    return issues_found

def run_kg_graph_validation(neo4j_client: Neo4jClient) -> list[dict]:
    """Runs Cypher queries to find structural contradictions or issues in the Neo4j Knowledge Graph."""
    print("⚖️ [T4-Consistency] Running Neo4j Cypher validation queries...")
    issues = []
    
    query_conflict = """
    MATCH (d1:Document)-[:CONTAINS_CONCEPT]->(c:Concept)<-[:CONTAINS_CONCEPT]-(d2:Document)
    WHERE d1.id < d2.id AND d1.department <> d2.department AND d1.status = 'active' AND d2.status = 'active'
    RETURN d1.id AS d1_id, d1.title AS d1_title, d2.id AS d2_id, d2.title AS d2_title, c.name AS concept_name
    LIMIT 20
    """
    try:
        conflicts = neo4j_client.run_query(query_conflict)
        for r in conflicts:
            issues.append({
                "type": "structural_conflict",
                "desc": f"Les documents '{r['d1_title']}' (Dept A) et '{r['d2_title']}' (Dept B) sont en conflit concernant le concept commun '{r['concept_name']}'."
            })
    except Exception as e:
        print(f"⚠️ [T4-Consistency] Neo4j Conflict query failed: {e}")

    query_orphans = """
    MATCH (c:Concept)
    WHERE NOT (c)<-[:CONTAINS_CONCEPT]-(:Document {status: 'active'})
    RETURN c.name AS concept_name
    LIMIT 20
    """
    try:
        orphans = neo4j_client.run_query(query_orphans)
        for r in orphans:
            issues.append({
                "type": "orphaned_concept",
                "desc": f"Le concept '{r['concept_name']}' est orphelin (aucun document actif ne le contient)."
            })
    except Exception as e:
        print(f"⚠️ [T4-Consistency] Neo4j Orphan query failed: {e}")

    return issues

def handle_message(topic, payload):
    print(f"⚖️ [T4-Consistency] Received event from {topic}: {payload}")
    db = SessionLocal()
    neo4j_client = Neo4jClient()
    vector_store = VectorStore()
    try:
        textual_issues = run_nli_scan(db, vector_store)
        for issue in textual_issues:
            exists = db.query(ConsistencyIssue).filter(
                ConsistencyIssue.chunk_a_id == issue["chunk_a_id"],
                ConsistencyIssue.chunk_b_id == issue["chunk_b_id"]
            ).first()
            
            if not exists:
                ci = ConsistencyIssue(
                    chunk_a_id=issue["chunk_a_id"],
                    chunk_b_id=issue["chunk_b_id"],
                    issue_type="contradiction",
                    confidence=issue["confidence"],
                    description=issue["description"]
                )
                db.add(ci)
                db.commit()
                db.refresh(ci)
                
                audit = AuditLog(
                    action="DETECT_CONTRADICTION",
                    service="t4-consistency-check",
                    details={"issue_id": str(ci.id), "confidence": issue["confidence"]},
                    explanation=f"Contradiction logique détectée entre deux segments de texte : {issue['description']}"
                )
                db.add(audit)
                db.commit()
                print(f"⚖️ [T4-Consistency] Saved consistency issue: {ci.id}")

        graph_issues = run_kg_graph_validation(neo4j_client)
        for issue in graph_issues:
            audit = AuditLog(
                action="DETECT_STRUCTURAL_ISSUE",
                service="t4-consistency-check",
                details={"type": issue["type"]},
                explanation=issue["desc"]
            )
            db.add(audit)
            db.commit()
            print(f"⚖️ [T4-Consistency] Graph structural issue logged: {issue['desc']}")
            
        producer = KafkaProducerWrapper()
        producer.publish("consistency.checked", {
            "textual_issues_count": len(textual_issues),
            "graph_issues_count": len(graph_issues),
            "timestamp": datetime.utcnow().isoformat()
        })
        producer.flush()
        print("⚖️ [T4-Consistency] Consistency check completed, event published.")

    except Exception as e:
        print(f"⚠️ [T4-Consistency] Error in message handler: {e}")
        db.rollback()
    finally:
        db.close()
        neo4j_client.close()

if __name__ == "__main__":
    print("🚀 Starting T4 Consistency Check Service...")
    consumer = T4ConsistencyConsumer()
    consumer.consume(handle_message)
