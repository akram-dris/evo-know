# 2. Week 2 — AI Core: Implementing the 5 Task Microservices

> **Goal**: Implement the 5 AI-powered task microservices (T1–T5) as defined in docs.txt and the enriched process table (Section 1.4.2). Each task maps to a specific row in that table with precisely defined AI techniques.

---

## Day 1 (Mon): Task 1 — Prediction of Update Needs (Prédiction des besoins de mises à jour)

### Source Definition (Section 1.4.2, Sub-Process: Évaluation)

| Field               | Value                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Task (FR)**       | Prédiction proactive des besoins futurs en mise à jour                             |
| **AI Techniques**   | Time-series forecasting (LSTM, Prophet, ARIMA), NLP trend analysis                 |
| **Value Added**     | Anticipates obsolescence before it occurs, enabling preventive rather than corrective updates |

### 2.1.1 What This Microservice Does

This service consumes document metadata and access logs from PostgreSQL to predict **when a knowledge document will become obsolete**. It assigns each document an **Obsolescence Risk Score** from 0.0 (fresh) to 1.0 (likely obsolete).

### 2.1.2 Feature Engineering

The prediction model uses the following features per document:

| Feature                 | Source               | Description                                                        |
|-------------------------|----------------------|--------------------------------------------------------------------|
| `age_days`              | `documents.uploaded_at` | Days since document was uploaded                                 |
| `days_since_last_update`| `documents.last_updated` | Days since last modification                                    |
| `access_frequency_7d`   | `access_logs`        | Number of accesses in the last 7 days                             |
| `access_frequency_30d`  | `access_logs`        | Number of accesses in the last 30 days                            |
| `access_trend`          | `access_logs`        | Slope of access frequency over time (declining = likely obsolete) |
| `department_update_rate`| `documents`          | Average update frequency for documents in the same department     |
| `content_similarity_to_new` | FAISS + new docs | Max cosine similarity to recently ingested documents (high = superseded) |
| `keyword_freshness`     | NLP trend analysis   | Whether key terms in the document are trending or declining       |

### 2.1.3 Model Architecture

**Option A: Prophet (Primary — simpler, interpretable)**
```python
# backend/services/t1-prediction/app/models/prophet_model.py
from prophet import Prophet
import pandas as pd

class UpdateNeedPredictor:
    """
    Uses Facebook Prophet to forecast access frequency trends.
    A document whose predicted access drops below a threshold is flagged.
    """
    def predict_obsolescence(self, document_id: str) -> float:
        # 1. Query access_logs for this document over time
        # 2. Create time-series DataFrame: ds (date), y (daily_access_count)
        # 3. Fit Prophet model
        # 4. Forecast 30 days ahead
        # 5. If forecasted access drops below threshold → high obsolescence score
        df = self._get_access_timeseries(document_id)
        model = Prophet(yearly_seasonality=False, weekly_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        predicted_trend = forecast['yhat'].iloc[-30:].mean()
        current_trend = df['y'].iloc[-30:].mean() if len(df) >= 30 else df['y'].mean()
        
        # Score: ratio of decline
        if current_trend == 0:
            return 0.8  # No access at all = high risk
        decline_ratio = max(0, (current_trend - predicted_trend) / current_trend)
        return min(1.0, decline_ratio * 1.5)  # Amplify slightly
```

**Option B: LSTM (Advanced — if enough data)**
```python
# backend/services/t1-prediction/app/models/lstm_model.py
import torch
import torch.nn as nn

class LSTMPredictor(nn.Module):
    """
    LSTM network for multi-feature time-series prediction.
    Input: sequence of [age, access_freq, similarity, keyword_freshness] over N days
    Output: obsolescence probability (0–1)
    """
    def __init__(self, input_size=4, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        out = self.fc(h_n[-1])
        return self.sigmoid(out)
```

### 2.1.4 Scoring Logic
```python
# backend/services/t1-prediction/app/scoring.py
def compute_obsolescence_score(document_id: str) -> dict:
    """
    Combines multiple signals into a single Obsolescence Risk Score.
    Returns: {"document_id": ..., "score": 0.73, "factors": {...}}
    """
    age_score = compute_age_factor(document_id)           # 0–1
    access_score = prophet_predictor.predict(document_id)  # 0–1
    similarity_score = check_superseded(document_id)       # 0–1
    
    # Weighted combination
    final_score = (0.3 * age_score + 0.5 * access_score + 0.2 * similarity_score)
    
    return {
        "document_id": document_id,
        "score": round(final_score, 3),
        "factors": {
            "age_factor": age_score,
            "access_trend_factor": access_score,
            "superseded_factor": similarity_score
        }
    }
```

### 2.1.5 Kafka Integration
- **Consumes**: `document.ingested`, `access.logged` events (trigger re-evaluation)
- **Produces**: `prediction.scored` event with the obsolescence score
- **Scheduled**: Also runs a daily batch scan of all active documents

### 2.1.6 Dataset Requirements
- **Training data**: Historical access logs (can be synthetically generated for testing)
- **Format**: Time-series CSV with columns: `date, document_id, access_count`
- **Volume**: At least 90 days of simulated data for 20+ documents

**Deliverable**: A microservice that scores every document's obsolescence risk and publishes results.

---

## Day 2 (Tue): Task 2 — Automatic Report Generation (Génération automatique des rapports de mise à jour)

### Source Definition (Section 1.4.2, Sub-Process: Évaluation)

| Field               | Value                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Task (FR)**       | Génération automatique de rapports d'évaluation et de tableaux de bord IA          |
| **AI Techniques**   | LLM for Natural Language Generation (NLG), BI augmented by AI, AI-driven dashboard generation |
| **Value Added**     | Produces evaluation reports understandable by managers, without analyst intervention |

### 2.2.1 What This Microservice Does

Consumes outputs from all other tasks (T1 scores, T3 fusions, T4 issues, T5 discoveries) and generates structured, human-readable Markdown reports using an LLM.

### 2.2.2 Report Types

| Report Type       | Trigger                       | Content                                                                |
|-------------------|-------------------------------|------------------------------------------------------------------------|
| `weekly_summary`  | Scheduled (every Friday)      | Summary of all KM activity: new docs, obsolescence alerts, fusions     |
| `alert_report`    | When T1 score > 0.7           | Urgent: specific document flagged as likely obsolete                    |
| `fusion_report`   | After T3 completes a merge    | Details of which chunks were merged and why                            |
| `consistency_report` | After T4 finds contradictions | List of detected contradictions with explanations                    |
| `discovery_report`| After T5 finds new relations  | Newly discovered relationships between concepts                        |

### 2.2.3 LLM-Based NLG Pipeline

```python
# backend/services/t2-report-generation/app/generators/nlg_report.py
import google.generativeai as genai

class ReportGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_weekly_report(self, data: dict) -> str:
        prompt = f"""
You are a Knowledge Management reporting assistant for an enterprise.
Generate a professional weekly KM update report in Markdown format based on this data:

## Input Data:
- New documents ingested this week: {data['new_docs_count']}
- Documents flagged as potentially obsolete (score > 0.7): {data['obsolete_docs']}
- Knowledge fusions performed: {data['fusions']}
- Consistency issues detected: {data['consistency_issues']}
- New knowledge relations discovered: {data['discoveries']}

## Report Structure:
1. Executive Summary (2-3 sentences)
2. New Knowledge Added (list with departments)
3. Obsolescence Alerts (table with document name, score, recommended action)
4. Knowledge Quality Updates (fusions, consistency fixes)
5. Knowledge Discovery Highlights
6. Recommendations for Next Week

Keep it professional, concise, and actionable. Use tables where appropriate.
"""
        response = self.model.generate_content(prompt)
        return response.text
```

### 2.2.4 Structured Dashboard Data
```python
# backend/services/t2-report-generation/app/generators/dashboard.py
def generate_dashboard_metrics() -> dict:
    """
    Aggregates data for a structured dashboard view.
    This data is sent to Slack as formatted Block Kit messages.
    """
    return {
        "total_documents": count_active_documents(),
        "avg_obsolescence_score": avg_score(),
        "high_risk_count": count_high_risk(threshold=0.7),
        "fusions_this_week": count_fusions_this_week(),
        "consistency_issues_open": count_open_issues(),
        "discoveries_this_week": count_discoveries(),
        "department_breakdown": get_department_stats()
    }
```

### 2.2.5 Kafka Integration
- **Consumes**: `prediction.scored`, `fusion.completed`, `consistency.checked`, `discovery.found`
- **Produces**: `report.generated` event (triggers system alerts / webhooks)

**Deliverable**: A microservice that auto-generates rich reports and dashboard data.

---

## Day 3 (Wed): Task 3 — Intelligent Knowledge Fusion (Fusion intelligente de connaissances)

### Source Definition (Section 1.4.2, Sub-Process: Changement & Raffinement)

| Field               | Value                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Task (FR)**       | Fusion intelligente de connaissances redondantes (Jointure automatisée)             |
| **AI Techniques**   | Semantic clustering (K-Means on embeddings, DBSCAN), NLP deduplication, Ontology alignment |
| **Value Added**     | Reduces redundancy by intelligently merging semantic duplicates                     |

### 2.3.1 What This Microservice Does

Identifies and merges redundant or overlapping knowledge chunks in the database. This directly implements the "Division/Jointure de paquets" activity from the original Change & Refinement sub-process, but now automated via AI.

### 2.3.2 Pipeline

```
Step 1: Fetch all active embeddings from FAISS
    ↓
Step 2: Compute pairwise cosine similarity
    ↓
Step 3: Cluster similar chunks (DBSCAN with eps=0.15)
    ↓
Step 4: For each cluster with >1 member:
    a. Flag as "potential duplicates"
    b. Use LLM to generate a merged summary
    c. Replace original chunks with merged version
    ↓
Step 5: Update Knowledge Graph (merge concept nodes)
    ↓
Step 6: Publish fusion.completed event
```

### 2.3.3 Semantic Clustering

```python
# backend/services/t3-knowledge-fusion/app/clustering/semantic_cluster.py
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

class SemanticClusterer:
    def __init__(self, similarity_threshold=0.85, min_samples=2):
        """
        similarity_threshold: chunks with cosine similarity >= this are candidates
        min_samples: DBSCAN parameter — minimum cluster size
        """
        self.eps = 1 - similarity_threshold  # DBSCAN uses distance, not similarity
        self.min_samples = min_samples

    def find_duplicate_clusters(self, embeddings: np.ndarray, chunk_ids: list[str]):
        # DBSCAN with precomputed distance matrix
        distance_matrix = 1 - cosine_similarity(embeddings)
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='precomputed')
        labels = clustering.fit_predict(distance_matrix)
        
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue  # Not a duplicate
            clusters.setdefault(label, []).append(chunk_ids[idx])
        
        return clusters  # {cluster_id: [chunk_id_1, chunk_id_2, ...]}
```

### 2.3.4 LLM-Assisted Merging

```python
# backend/services/t3-knowledge-fusion/app/merger.py
class KnowledgeMerger:
    def merge_chunks(self, chunks: list[str]) -> str:
        """Uses an LLM to create a single comprehensive version from duplicate chunks."""
        prompt = f"""
You are a knowledge management system. The following {len(chunks)} text segments 
contain overlapping or redundant information. Merge them into a single, comprehensive, 
non-redundant paragraph that preserves ALL unique information:

{chr(10).join([f'--- Segment {i+1} ---{chr(10)}{c}' for i, c in enumerate(chunks)])}

Output ONLY the merged text, nothing else.
"""
        response = self.llm.generate_content(prompt)
        return response.text
```

### 2.3.5 Dataset Requirements
- **Test data**: Deliberately create 5–10 pairs of semantically similar but differently-worded documents.
- **Evaluation**: Measure reduction in total chunks and verify no information loss via manual review.

**Deliverable**: A deduplication microservice that clusters, merges, and cleans the knowledge base.

---

## Day 4 (Thu): Task 4 — Automatic Consistency Analysis (Analyse automatique de cohérence)

### Source Definition (Section 1.4.2, Sub-Process: Changement & Raffinement)

| Field               | Value                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Task (FR)**       | Vérification automatique de la cohérence des connaissances                         |
| **AI Techniques**   | Inference engines, NLP, Knowledge Graphs                                           |
| **Value Added**     | Automatically detects and flags inconsistencies and contradictions in the knowledge repository |

### 2.4.1 What This Microservice Does

Scans the knowledge base for contradictions, outdated information, and logical inconsistencies. Uses two complementary approaches:

1. **NLI-based detection**: Uses a Natural Language Inference model (BERT-based) to classify pairs of statements as `entailment`, `neutral`, or `contradiction`.
2. **Knowledge Graph validation**: Cross-references facts in the graph to detect structural inconsistencies.

### 2.4.2 NLI-Based Contradiction Detection

```python
# backend/services/t4-consistency-check/app/analyzers/nli_checker.py
from transformers import pipeline

class NLIConsistencyChecker:
    def __init__(self):
        self.nli = pipeline(
            "text-classification",
            model="cross-encoder/nli-deberta-v3-base",
            device=-1  # CPU
        )

    def check_pair(self, text_a: str, text_b: str) -> dict:
        """
        Checks if two knowledge chunks contradict each other.
        Returns: {"label": "contradiction"|"entailment"|"neutral", "score": 0.95}
        """
        result = self.nli(f"{text_a} [SEP] {text_b}")
        return result[0]

    def scan_all_pairs(self, chunks: list[dict], similarity_threshold=0.6):
        """
        Only check pairs that are topically similar (cosine sim > threshold)
        to avoid O(n²) comparisons on unrelated chunks.
        """
        contradictions = []
        for i, chunk_a in enumerate(chunks):
            for j, chunk_b in enumerate(chunks):
                if i >= j:
                    continue
                # Only check if embeddings are similar enough (same topic)
                sim = cosine_similarity(chunk_a['embedding'], chunk_b['embedding'])
                if sim < similarity_threshold:
                    continue
                result = self.check_pair(chunk_a['content'], chunk_b['content'])
                if result['label'] == 'contradiction' and result['score'] > 0.8:
                    contradictions.append({
                        'chunk_a_id': chunk_a['id'],
                        'chunk_b_id': chunk_b['id'],
                        'confidence': result['score'],
                        'text_a': chunk_a['content'][:200],
                        'text_b': chunk_b['content'][:200]
                    })
        return contradictions
```

### 2.4.3 Knowledge Graph Validation

```python
# backend/services/t4-consistency-check/app/analyzers/kg_validator.py
class KGValidator:
    def find_structural_issues(self):
        """
        Cypher queries to detect structural inconsistencies in the Knowledge Graph.
        """
        queries = {
            # Documents claiming contradictory facts about same concept
            "contradicting_documents": """
                MATCH (d1:Document)-[:CONTAINS_CONCEPT]->(c:Concept)<-[:CONTAINS_CONCEPT]-(d2:Document)
                WHERE d1.id < d2.id
                AND d1.department <> d2.department
                AND d1.status = 'active' AND d2.status = 'active'
                RETURN d1.title, d2.title, c.name
            """,
            # Orphaned concepts (no document reference)
            "orphaned_concepts": """
                MATCH (c:Concept)
                WHERE NOT (c)<-[:CONTAINS_CONCEPT]-(:Document {status: 'active'})
                RETURN c.name
            """,
            # Circular supersession chains
            "circular_supersession": """
                MATCH path = (d1:Document)-[:SUPERSEDES*2..5]->(d1)
                RETURN path
            """
        }
        # Execute each query and collect issues
        ...
```

### 2.4.4 Consistency Report Output
```json
{
  "scan_timestamp": "2026-05-20T10:00:00Z",
  "total_pairs_checked": 1250,
  "contradictions_found": 3,
  "issues": [
    {
      "type": "contradiction",
      "chunk_a": "The company uses PostgreSQL 14 for all production databases.",
      "chunk_b": "All production systems run on MySQL 8.0.",
      "confidence": 0.94,
      "recommendation": "Review and resolve: which database is used in production?"
    }
  ]
}
```

### 2.4.5 Kafka Integration
- **Consumes**: `document.ingested`, `fusion.completed` (check after new data or merge)
- **Produces**: `consistency.checked` with issue details

**Deliverable**: A consistency analysis service that detects contradictions using both NLI and graph validation.

---

## Day 5 (Fri): Task 5 — Automatic Knowledge Discovery (Découverte automatique de connaissances)

### Source Definition (Section 1.4.2, Sub-Process: Développement)

| Field               | Value                                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Task (FR)**       | Découverte automatique de relations cachées (Knowledge Discovery)                  |
| **AI Techniques**   | Data mining (Association Rule Mining — Apriori, FP-Growth), GNN for link discovery, Text Mining / NER |
| **Value Added**     | Reveals non-obvious relationships between knowledge, opening new business approaches and innovations |

### 2.5.1 What This Microservice Does

Discovers hidden relationships between knowledge entities that are not explicitly stated. Uses three complementary techniques:

1. **NER (Named Entity Recognition)**: Extracts entities (people, technologies, processes) from text.
2. **Association Rule Mining**: Finds co-occurrence patterns (e.g., "documents mentioning Topic A often also mention Topic B").
3. **Link Prediction on the Knowledge Graph**: Predicts missing edges between concept nodes.

### 2.5.2 Named Entity Recognition

```python
# backend/services/t5-knowledge-discovery/app/mining/ner_extractor.py
from transformers import pipeline

class NERExtractor:
    def __init__(self):
        # Using a multilingual NER model (French/English support)
        self.ner = pipeline(
            "ner",
            model="Jean-Baptiste/camembert-ner",  # French NER
            aggregation_strategy="simple"
        )

    def extract_entities(self, text: str) -> list[dict]:
        """
        Extracts named entities from text.
        Returns: [{"entity": "Mobilis", "type": "ORG", "score": 0.98}, ...]
        """
        entities = self.ner(text)
        return [
            {
                "entity": e["word"],
                "type": e["entity_group"],  # PER, ORG, LOC, MISC
                "score": e["score"]
            }
            for e in entities if e["score"] > 0.7
        ]
```

### 2.5.3 Association Rule Mining

```python
# backend/services/t5-knowledge-discovery/app/mining/relation_miner.py
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

class RelationMiner:
    def mine_concept_associations(self, documents: list[dict]) -> pd.DataFrame:
        """
        Finds which concepts frequently co-occur in documents.
        Uses Apriori algorithm on a binary concept-document matrix.
        """
        # Build binary matrix: rows=documents, columns=concepts
        all_concepts = set()
        for doc in documents:
            all_concepts.update(doc['concepts'])
        
        matrix = []
        for doc in documents:
            row = {c: (c in doc['concepts']) for c in all_concepts}
            matrix.append(row)
        
        df = pd.DataFrame(matrix)
        
        # Find frequent itemsets
        frequent = apriori(df, min_support=0.1, use_colnames=True)
        
        # Generate association rules
        rules = association_rules(frequent, metric="lift", min_threshold=1.5)
        
        return rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
```

### 2.5.4 Knowledge Graph Link Prediction

```python
# backend/services/t5-knowledge-discovery/app/mining/gnn_discovery.py
class LinkPredictor:
    def predict_missing_links(self):
        """
        Uses graph structure to predict potential but missing relationships.
        Simple approach: common neighbors + Jaccard coefficient.
        Advanced (if feasible): GNN-based link prediction (PyTorch Geometric).
        """
        query = """
        // Find concept pairs that share multiple document connections
        // but have no direct RELATED_TO edge
        MATCH (c1:Concept)<-[:CONTAINS_CONCEPT]-(d:Document)-[:CONTAINS_CONCEPT]->(c2:Concept)
        WHERE c1.name < c2.name
        AND NOT (c1)-[:RELATED_TO]-(c2)
        WITH c1, c2, COUNT(DISTINCT d) AS shared_docs
        WHERE shared_docs >= 3
        RETURN c1.name AS concept_a, c2.name AS concept_b, shared_docs
        ORDER BY shared_docs DESC
        LIMIT 20
        """
        # Execute and create RELATED_TO edges for discovered links
        ...
```

### 2.5.5 Pipeline Integration
```
Step 1: For each new document:
    → Run NER to extract entities
    → Store entities as Concept nodes in Neo4j
    → Link to the Document node
    ↓
Step 2: Periodically (daily):
    → Build concept-document matrix
    → Run Apriori to find association rules
    → For rules with high lift: create RELATED_TO edges in Neo4j
    ↓
Step 3: Run link prediction
    → Find concept pairs sharing many documents but not linked
    → Suggest new RELATED_TO edges
    ↓
Step 4: Publish discovery.found event
```

### 2.5.6 Kafka Integration
- **Consumes**: `document.ingested` (extract entities from new docs)
- **Produces**: `discovery.found` (new relationship discovered)

**Deliverable**: A knowledge discovery service that extracts entities, mines associations, and enriches the knowledge graph.

---

## Weekend (Sat–Sun): Integration & Testing

### Integration Tasks:
1. **Wire all 5 services to Kafka**:
   - Test the full event chain: `document.ingested` → T5 (NER) → T3 (fusion check) → T4 (consistency check) → T1 (scoring) → T2 (report)
2. **End-to-end test**:
   - Ingest 5 documents through the API Gateway
   - Verify T5 extracts entities
   - Verify T3 identifies duplicates (if any)
   - Verify T4 runs NLI checks
   - Verify T1 computes scores
   - Verify T2 generates a report
3. **Unit tests** per service (pytest)
4. **Fix bugs** discovered during integration

### Week 2 Exit Criteria:
- [ ] T1 assigns obsolescence scores to all documents
- [ ] T2 generates a valid Markdown report from aggregated data
- [ ] T3 identifies and merges at least 2 redundant chunk clusters
- [ ] T4 detects at least 1 planted contradiction in test data
- [ ] T5 extracts entities and discovers at least 3 association rules
- [ ] All services communicate via Kafka events
- [ ] All outputs are persisted in PostgreSQL
