# 5. Task-to-Thesis Traceability Matrix

> This document maps every implementation artifact back to its theoretical source in the thesis documents, ensuring **full traceability** between the academic requirements and the engineering deliverables.

---

## 5.1 Source Documents Referenced

| ID    | Document                                                                         | Description                                                    |
|-------|----------------------------------------------------------------------------------|----------------------------------------------------------------|
| SRC-1 | `CHIKHI Imane_Proposition Sujet Master IL_2025-2026-Sujet 2.pdf`                 | Official thesis proposal by the supervisor                     |
| SRC-2 | `Mémoire_Mis_en_œuvre_d'un_système_basé_Cloud_pour_le_partage_des.pdf` (Ikram)   | Previous Master memoir — Knowledge Sharing system              |
| SRC-3 | `1.docx` (Enriched Chapter 1)                                                    | New chapter with AI-KM state of the art and enriched update process |
| SRC-4 | `docs.txt`                                                                        | Supervisor's instructions for the 5 selected tasks             |
| SRC-5 | `image copy 2.png`                                                                | Cloud Native architecture diagram provided by supervisor       |
| SRC-6 | `image.png` + `image copy.png`                                                    | Supervisor's email screenshots with additional instructions    |

---

## 5.2 Requirement Traceability

### From Thesis Proposal (SRC-1)

| Requirement (FR)                                                                 | Section in SRC-1    | Implementation                                 |
|----------------------------------------------------------------------------------|---------------------|-------------------------------------------------|
| Intégration de techniques de l'IA dans le processus de mise à jour               | Objectifs           | T1–T5 microservices (Week 2)                    |
| Architecture Cloud Native                                                         | Plan de Travail §3  | Docker + Microservices (Week 1, Day 2)          |
| Interopérabilité avec le système organisationnel d'entreprise                    | Objectifs + §1,§2   | REST API + Webhooks (Week 4, Day 1)             |
| Mise en œuvre du système basé Deep Learning                                       | Plan de Travail §3  | LSTM model in T1, NLI in T4 (Week 2)           |

### From Supervisor's Instructions (SRC-4, SRC-6)

| Instruction                                                                       | Source              | Implementation                                 |
|-----------------------------------------------------------------------------------|---------------------|-------------------------------------------------|
| "Nous adoptons une architecture Cloud Native pour le système"                     | SRC-4, line 3       | Docker Compose + Microservices                  |
| "Chaque micro-service implémente une fonctionnalité du système"                   | SRC-4, line 5       | 5 task services + gateway + bot + orchestrator  |
| "Prédiction des besoins de mises à jour"                                          | SRC-4, line 10      | `t1-prediction/` service                        |
| "Génération automatique des rapports de mise à jour"                              | SRC-4, line 11      | `t2-report-generation/` service                 |
| "Fusion intelligente de connaissances"                                             | SRC-4, line 12      | `t3-knowledge-fusion/` service                  |
| "Analyse automatique de cohérence"                                                 | SRC-4, line 13      | `t4-consistency-check/` service                 |
| "Découverte automatique de connaissances"                                          | SRC-4, line 14      | `t5-knowledge-discovery/` service               |
| "On se base sur les techniques d'IA associées à chaque tâche" (from the table)    | SRC-4, line 16      | AI techniques mapped per task (see §5.3)        |
| "Les datasets dépendent des techniques d'IA"                                       | SRC-6 (email)       | Dataset requirements per task (Week 2 docs)     |

### From Enriched Process Table (SRC-3, Section 1.4.2)

| Sub-Process        | Task                                         | AI Techniques (from table)                                      | Implemented In           |
|--------------------|----------------------------------------------|-----------------------------------------------------------------|--------------------------|
| Évaluation         | Prédiction proactive des besoins futurs      | LSTM, Prophet, ARIMA, NLP trend analysis                        | `t1-prediction/`         |
| Évaluation         | Génération auto de rapports/tableaux de bord | LLM NLG, BI augmentée AI, AI-driven dashboards                 | `t2-report-generation/`  |
| Changement & Raff. | Fusion intelligente de connaissances         | K-Means embeddings, DBSCAN, NLP dedup, ontology alignment      | `t3-knowledge-fusion/`   |
| Changement & Raff. | Vérification auto cohérence                  | Inference engines, NLP, Knowledge Graphs                        | `t4-consistency-check/`  |
| Développement      | Découverte auto relations cachées            | Apriori, FP-Growth, GNN link discovery, Text Mining, NER       | `t5-knowledge-discovery/`|

### From Architecture Diagram (SRC-5)

| Component in Diagram                              | Implementation                              |
|---------------------------------------------------|---------------------------------------------|
| API Gateway - Entrée Unique                        | `backend/services/api-gateway/` (FastAPI)   |
| Event Bus / Message Broker (Kafka, RabbitMQ)       | Kafka in Docker Compose                     |
| Tâche 1: Service de Prédiction des besoins de MàJ | `backend/services/t1-prediction/`           |
| Tâche 2: Service de Génération auto des rapports   | `backend/services/t2-report-generation/`    |
| Tâche 3: Service de Fusion intelligente            | `backend/services/t3-knowledge-fusion/`     |
| Tâche 4: Service de Analyse auto de cohérence      | `backend/services/t4-consistency-check/`    |
| Tâche 5: Service de Découverte auto de connaissances| `backend/services/t5-knowledge-discovery/`  |
| Base de Connaissances Centralisée                  | PostgreSQL + FAISS + Neo4j                  |
| Données de Référence                               | `documents` + `knowledge_chunks` tables     |
| Métadonnées                                         | `obsolescence_scores`, `audit_log`, etc.    |
| Service Registry (Consul)                          | Consul container (Docker Compose)           |
| Monitoring & Logging (ELK, Prometheus)             | Prometheus + ELK in Docker Compose          |
| CI/CD Pipeline                                      | GitHub Actions                               |
| Sources de Connaissances Externes                  | Ingestion API + parsers                     |
| Utilisateurs Finaux / Systèmes Aval               | Vue.js 3 Web Application + REST API + Webhooks |

### From Previous Memoir (SRC-2)

| Element from Ikram's Work                          | How We Build Upon It                         |
|---------------------------------------------------|---------------------------------------------|
| 4 sub-processes of update (Enrichment, Change & Refinement, Evaluation, Development) | Retained + augmented with AI techniques     |
| Cloud Native architecture (Spring Boot, Eureka, Docker) | Same pattern but Python + FastAPI + Kafka   |
| Enterprise validation with Mobilis OSS department  | Same validation approach                     |
| Service Registry (Eureka)                          | Replaced with Consul (as in SRC-5 diagram)  |
| Prometheus for monitoring                          | Retained                                     |
| Docker for containerization                        | Retained                                     |
| Proposed 5th sub-process: AI Orchestration         | Fully implemented (SRC-3, Section 1.4.3)    |

---

## 5.3 AI Technique ↔ Python Implementation Mapping

| AI Technique                              | Python Library / Model                        | Service         | File                          |
|-------------------------------------------|----------------------------------------------|-----------------|-------------------------------|
| LSTM time-series forecasting              | `torch.nn.LSTM`                              | T1              | `models/lstm_model.py`        |
| Prophet forecasting                       | `prophet.Prophet`                            | T1              | `models/prophet_model.py`     |
| NLG report generation                     | `google.generativeai` (Gemini API)           | T2              | `generators/nlg_report.py`    |
| K-Means clustering on embeddings          | `sklearn.cluster.KMeans`                     | T3              | `clustering/semantic_cluster.py` |
| DBSCAN clustering                         | `sklearn.cluster.DBSCAN`                     | T3              | `clustering/semantic_cluster.py` |
| NLP deduplication                         | Cosine similarity on sentence embeddings     | T3              | `clustering/deduplication.py` |
| NLI contradiction detection               | `cross-encoder/nli-deberta-v3-base`          | T4              | `analyzers/nli_checker.py`    |
| Knowledge Graph validation                | Neo4j Cypher queries                         | T4              | `analyzers/kg_validator.py`   |
| Named Entity Recognition (NER)            | `Jean-Baptiste/camembert-ner`                | T5              | `mining/ner_extractor.py`     |
| Association Rule Mining (Apriori)         | `mlxtend.frequent_patterns.apriori`          | T5              | `mining/relation_miner.py`    |
| Sentence Embeddings                       | `sentence-transformers` (MiniLM)             | Shared          | `embeddings/encoder.py`       |
| RAG (Retrieval-Augmented Generation)      | FAISS + Gemini API                           | Vue Frontend    | `components/widgets/RAGChatbot.vue`           |

---

## 5.4 Kafka Event Flow Map

```
document.ingested
    ├── → t5-knowledge-discovery (extract entities)
    ├── → t3-knowledge-fusion (check for duplicates)
    ├── → t4-consistency-check (validate new content)
    └── → t1-prediction (update scores for all docs)

discovery.found
    └── → t2-report-generation (include in next report)

fusion.completed
    ├── → t4-consistency-check (re-check after merge)
    └── → t2-report-generation (include in next report)

consistency.checked
    ├── → orchestrator (decide: auto-resolve or escalate)
    └── → t2-report-generation (include in next report)

prediction.scored
    ├── → orchestrator (alert if score > threshold)
    └── → t2-report-generation (include in next report)

report.generated
    └── → DB / SSE (retrieved by Vue reports view)

orchestrator.alert
    └── → DB / SSE (displayed in Vue active alerts dashboard)
```

---

## 5.5 Database Table ↔ KM Sub-Process Mapping

| Table                  | KM Sub-Process                   | Task  | Purpose                                          |
|------------------------|----------------------------------|-------|--------------------------------------------------|
| `documents`            | All                              | —     | Core knowledge asset registry                    |
| `knowledge_chunks`     | All                              | —     | Processed text segments for AI processing        |
| `obsolescence_scores`  | Évaluation                       | T1    | Prediction results                               |
| `update_reports`       | Évaluation                       | T2    | Generated report storage                         |
| `fusion_events`        | Changement & Raffinement         | T3    | Record of all merges performed                   |
| `consistency_issues`   | Changement & Raffinement         | T4    | Detected contradictions                          |
| `discovered_relations` | Développement                    | T5    | Newly discovered concept relationships           |
| `audit_log`            | AI Orchestration (5th sub-proc)  | Orch  | XAI traceability for all automated decisions     |
| `access_logs`          | Évaluation                       | T1    | Input data for prediction model                  |

---

## 5.6 Validation ↔ Thesis Defense Mapping

| Defense Question                                           | Evidence to Present                                         |
|-----------------------------------------------------------|-------------------------------------------------------------|
| "How does your system implement Cloud Native?"            | Docker Compose, microservice separation, Kafka event bus    |
| "What AI techniques did you use?"                         | Section 5.3 table above + code demonstrations               |
| "How is this different from the previous work?"           | 5th sub-process (Orchestrator), AI automation, Vue Web UI   |
| "How does interoperability work?"                         | REST API + Swagger UI + Webhook demo                        |
| "What datasets did you use?"                              | Synthetic enterprise documents + access logs                |
| "What are your evaluation metrics?"                       | Section 4.4.2 metrics table + actual measurements           |
| "How do you ensure traceability?"                         | audit_log table with XAI explanations + demo query          |
