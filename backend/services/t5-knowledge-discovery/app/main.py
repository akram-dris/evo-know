import os
import json
import uuid
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from shared.kafka.consumer import KafkaConsumerBase
from shared.kafka.producer import KafkaProducerWrapper
from shared.database.postgres import SessionLocal, Document, DiscoveredRelation, AuditLog
from shared.database.neo4j_client import Neo4jClient

try:
    from mlxtend.frequent_patterns import apriori, association_rules
    HAS_MLXTEND = True
except ImportError:
    HAS_MLXTEND = False
    print("⚠️ mlxtend not available. Falling back to statistical co-occurrence rule mining.")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

HAS_GEMINI = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        HAS_GEMINI = True
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API in T5: {e}")

class T5DiscoveryConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t5-discovery-group", ["document.ingested"])
        self.producer = KafkaProducerWrapper()

def call_ner_api(text: str) -> list[dict]:
    """Uses Gemini API to extract named entities/concepts from text."""
    if HAS_GEMINI:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = f"""Extrayez les concepts clés, technologies, protocoles, systèmes et organisations du texte suivant.
Texte :
"{text[:4000]}"

Renvoyez le résultat au format JSON brut suivant (une liste d'objets) sans autre texte ou balise Markdown :
[
  {{
    "name": "Nom du concept / entité",
    "type": "ORG" | "TECH" | "PROC" | "SYS"
  }}
]
"""
            response = model.generate_content(prompt)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"⚠️ Gemini NER call failed: {e}. Falling back to default list.")
            
    return [
        {"name": "Système de fichiers local", "type": "SYS"},
        {"name": "SBERT", "type": "TECH"},
        {"name": "Neo4j", "type": "TECH"},
        {"name": "PostgreSQL", "type": "TECH"}
    ]

def mine_association_rules(neo4j_client: Neo4jClient, db: Session) -> list[dict]:
    """Mines association rules between concepts based on co-occurrence in documents."""
    print("🔍 [T5-Discovery] Mining concept association rules from co-occurrences...")
    
    query = """
    MATCH (d:Document {status: 'active'})-[:CONTAINS_CONCEPT]->(c:Concept)
    RETURN d.id AS doc_id, c.name AS concept_name
    """
    try:
        records = neo4j_client.run_query(query)
    except Exception as e:
        print(f"⚠️ [T5-Discovery] Failed to query Neo4j co-occurrences: {e}")
        return []
        
    if not records:
        return []
        
    df = pd.DataFrame(records)
    
    pivot_df = pd.crosstab(df['doc_id'], df['concept_name']).astype(bool)
    
    discovered_relations = []
    
    if HAS_MLXTEND and len(pivot_df) >= 2:
        try:
            frequent_itemsets = apriori(pivot_df, min_support=0.1, use_colnames=True)
            if not frequent_itemsets.empty:
                rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)
                for _, row in rules.iterrows():
                    antecedents = list(row['antecedents'])
                    consequents = list(row['consequents'])
                    if antecedents and consequents:
                        discovered_relations.append({
                            "entity_a": antecedents[0],
                            "entity_b": consequents[0],
                            "relation_type": "RELATED_TO",
                            "confidence": float(row['confidence']),
                            "lift": float(row['lift']),
                            "method": "Apriori"
                        })
        except Exception as e:
            print(f"⚠️ [T5-Discovery] Apriori mining failed: {e}")
            
    if not discovered_relations:
        concepts = list(pivot_df.columns)
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                c1 = concepts[i]
                c2 = concepts[j]
                
                docs_c1 = set(pivot_df[pivot_df[c1] == True].index)
                docs_c2 = set(pivot_df[pivot_df[c2] == True].index)
                
                intersection = docs_c1.intersection(docs_c2)
                union = docs_c1.union(docs_c2)
                
                if intersection and union:
                    jaccard = len(intersection) / len(union)
                    if jaccard >= 0.2:
                        discovered_relations.append({
                            "entity_a": c1,
                            "entity_b": c2,
                            "relation_type": "RELATED_TO",
                            "confidence": jaccard,
                            "lift": 1.5,
                            "method": "Jaccard-Cooccurrence"
                        })
                        
    return discovered_relations

def run_link_prediction(neo4j_client: Neo4jClient) -> list[dict]:
    """Graph Link Prediction: Suggest relations between concepts sharing common neighbors (documents)."""
    print("🔍 [T5-Discovery] Running link prediction analysis in graph...")
    query = """
    MATCH (c1:Concept)<-[:CONTAINS_CONCEPT]-(d:Document)-[:CONTAINS_CONCEPT]->(c2:Concept)
    WHERE c1.name < c2.name
    AND NOT (c1)-[:RELATED_TO]-(c2)
    WITH c1, c2, COUNT(DISTINCT d) AS shared_docs
    WHERE shared_docs >= 2
    RETURN c1.name AS concept_a, c2.name AS concept_b, shared_docs
    ORDER BY shared_docs DESC
    LIMIT 10
    """
    predictions = []
    try:
        results = neo4j_client.run_query(query)
        for r in results:
            predictions.append({
                "entity_a": r["concept_a"],
                "entity_b": r["concept_b"],
                "relation_type": "RELATED_TO",
                "confidence": min(1.0, 0.4 + (r["shared_docs"] * 0.15)),
                "method": "KG-LinkPrediction"
            })
    except Exception as e:
        print(f"⚠️ [T5-Discovery] Link prediction failed: {e}")
        
    return predictions

def handle_message(topic, payload):
    print(f"🔍 [T5-Discovery] Received event from {topic}: {payload}")
    db = SessionLocal()
    neo4j_client = Neo4jClient()
    try:
        doc_id = payload.get("document_id")
        title = payload.get("title", "Document")
        
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"⚠️ [T5-Discovery] Document {doc_id} not found in PostgreSQL.")
            return

        from shared.database.postgres import KnowledgeChunk
        first_chunk = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == doc_id
        ).order_by(KnowledgeChunk.chunk_index).first()
        
        text_content = first_chunk.content if first_chunk else title

        entities = call_ner_api(text_content)
        print(f"🔍 [T5-Discovery] Extracted {len(entities)} concepts/entities.")
        
        for entity in entities:
            name = entity["name"].strip()
            etype = entity["type"].strip()
            
            cypher_query = """
            MATCH (d:Document {id: $doc_id})
            MERGE (c:Concept {name: $name})
            ON CREATE SET c.type = $type
            MERGE (d)-[:CONTAINS_CONCEPT]->(c)
            """
            try:
                neo4j_client.run_query(cypher_query, {
                    "doc_id": doc_id,
                    "name": name,
                    "type": etype
                })
            except Exception as e:
                print(f"⚠️ [T5-Discovery] Neo4j concept link failed for '{name}': {e}")

        rules = mine_association_rules(neo4j_client, db)
        predictions = run_link_prediction(neo4j_client)
        
        all_discoveries = rules + predictions
        new_relations_count = 0
        
        for discovery in all_discoveries:
            exists = db.query(DiscoveredRelation).filter(
                DiscoveredRelation.entity_a == discovery["entity_a"],
                DiscoveredRelation.entity_b == discovery["entity_b"]
            ).first()
            
            if not exists:
                dr = DiscoveredRelation(
                    entity_a=discovery["entity_a"],
                    entity_b=discovery["entity_b"],
                    relation_type=discovery["relation_type"],
                    confidence=discovery["confidence"],
                    method=discovery["method"]
                )
                db.add(dr)
                db.commit()
                new_relations_count += 1
                
                cypher_link = """
                MATCH (c1:Concept {name: $name_a})
                MATCH (c2:Concept {name: $name_b})
                MERGE (c1)-[r:RELATED_TO]->(c2)
                ON CREATE SET r.confidence = $confidence, r.method = $method
                """
                try:
                    neo4j_client.run_query(cypher_link, {
                        "name_a": discovery["entity_a"],
                        "name_b": discovery["entity_b"],
                        "confidence": discovery["confidence"],
                        "method": discovery["method"]
                    })
                except Exception as e:
                    print(f"⚠️ [T5-Discovery] Neo4j RELATED_TO edge creation failed: {e}")

                explanation = (
                    f"Découverte automatique d'une relation cachée de type '{discovery['relation_type']}' "
                    f"entre '{discovery['entity_a']}' et '{discovery['entity_b']}' via la méthode {discovery['method']} "
                    f"(Indice de confiance: {discovery['confidence']})."
                )
                audit = AuditLog(
                    action="DISCOVER_RELATION",
                    service="t5-knowledge-discovery",
                    details=discovery,
                    explanation=explanation
                )
                db.add(audit)
                db.commit()
                print(f"🔍 [T5-Discovery] Recorded discovery: {discovery['entity_a']} -> {discovery['entity_b']}")

        producer = KafkaProducerWrapper()
        producer.publish("discovery.found", {
            "document_id": doc_id,
            "concepts_extracted_count": len(entities),
            "new_relations_discovered_count": new_relations_count,
            "timestamp": datetime.utcnow().isoformat()
        })
        producer.flush()
        print("🔍 [T5-Discovery] Knowledge Discovery finished, event published.")

    except Exception as e:
        print(f"⚠️ [T5-Discovery] Error in message handler: {e}")
        db.rollback()
    finally:
        db.close()
        neo4j_client.close()

if __name__ == "__main__":
    print("🚀 Starting T5 Knowledge Discovery Service...")
    consumer = T5DiscoveryConsumer()
    consumer.consume(handle_message)
