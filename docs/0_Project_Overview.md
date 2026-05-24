# 0. Project Overview — Cloud-Native KM Update System

## 0.1 Academic Context

| Field           | Value                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------- |
| University      | Université Saad Dahlab — Blida 1, Faculty of Sciences, Department of Computer Science       |
| Degree          | Master's Thesis — Option: Software Engineering (Ingénierie de Logiciel)                     |
| Supervisor      | Mme CHIKHI Imane, Maître Assistante, Department of Computer Science                         |
| Full Title (FR) | Utilisation de techniques de l'IA pour la mise en œuvre d'un système interopérable de gestion de connaissances organisationnelles basé sur le Cloud Computing |
| Keywords        | Organizational Knowledge, Knowledge Management, KM Processes, Knowledge Update Process, Interoperability, Cloud Computing, Cloud Native Architecture, AI Techniques |

## 0.2 Lineage of Prior Work

This project is a direct continuation of a research track initiated by Mme CHIKHI's doctoral thesis, which proposed:

1. **A Cloud-Based KM Framework** — An infrastructure founded on Cloud Computing to support all KM sub-processes (Identification, Acquisition, Formalization, Sharing, Utilization, Update, and Organizational Environment).
2. **Prior Master Projects** — Previous students implemented systems for the Identification, Acquisition, and Formalization sub-processes using Cloud Native architecture. Ikram's memoir (the immediate predecessor) implemented the **Knowledge Sharing Process** as a microservices system using Spring Boot, Eureka (Service Registry), Zipkin (Distributed Tracing), Docker, and Prometheus, validated against the OSS department of Mobilis.
3. **Ikram's Theoretical Contribution** — Proposed the first formal definition of the Knowledge Update Process, decomposed into 4 sub-processes: **Enrichment**, **Change & Refinement**, **Evaluation**, and **Development**. However, this definition was purely human-centered with no AI integration.

## 0.3 What THIS Project Must Do

As stated in the supervisor's instructions (docs.txt) and the email screenshots:

> "Il s'agit de développer un système mettant en œuvre le processus de mise à jour des connaissances que vous avez proposé."

The system must implement the **AI-enriched version** of the Knowledge Update Process proposed in the docx (Section 1.4.2), not the original human-only version from Ikram's memoir.

### 0.3.1 The 5 Selected Tasks

The supervisor confirmed (docs.txt) that it is **impossible to implement the entire process**. The selected tasks are:

| #  | Task Name (FR)                                         | Task Name (EN)                              | Parent Sub-Process       | AI Techniques (from Section 1.4.2 table)                                                               |
|----|-------------------------------------------------------|---------------------------------------------|--------------------------|--------------------------------------------------------------------------------------------------------|
| T1 | Prédiction des besoins de mises à jour                | Prediction of Update Needs                  | Évaluation               | Time-series forecasting (LSTM, Prophet, ARIMA), NLP trend analysis                                     |
| T2 | Génération automatique des rapports de mise à jour    | Automatic Generation of Update Reports      | Évaluation               | LLM for NLG, BI augmented by AI (AutoML + NLG), AI-driven dashboard generation                         |
| T3 | Fusion intelligente de connaissances                  | Intelligent Knowledge Fusion                | Changement & Raffinement | Semantic clustering (K-Means on embeddings, DBSCAN), NLP deduplication, Ontology alignment             |
| T4 | Analyse automatique de cohérence                      | Automatic Consistency Analysis              | Changement & Raffinement | Inference engines, NLP, Knowledge Graphs                                                                |
| T5 | Découverte automatique de connaissances               | Automatic Knowledge Discovery               | Développement            | Data mining (Apriori, FP-Growth), Graph Neural Networks (GNN) for link discovery, Text Mining / NER     |

### 0.3.2 The 5th Sub-Process: AI Orchestration

Our enriched proposal introduces a novel 5th sub-process: **Automation & Orchestration by AI**. In this implementation, it manifests as a background orchestrator service that:
- Sequences the 5 task-specific microservices.
- Monitors the knowledge base for anomalies and triggers external alerts/webhooks.
- Resolves conflicts between concurrent knowledge versions.
- Provides traceability (audit log) of every automated decision using Explainable AI (XAI) principles.

### 0.3.3 Datasets

As confirmed by the supervisor's email:
> "Pour tester, on doit utiliser des datasets. Cependant, en faisant des recherches, les datasets dépendent des techniques d'IA. Certaines techniques exigent des structures bien précises pour fonctionner."

Datasets will be selected and structured per-task, based on each AI technique's requirements. They will be discussed with the supervisor as the implementation progresses.

## 0.4 Technology Stack

| Layer                      | Technology                                                                                    | Justification                                                                                             |
|----------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Language**               | Python 3.10+                                                                                  | De facto standard for AI/ML, rich ecosystem (PyTorch, HuggingFace, LangChain)                             |
| **Web Framework**          | FastAPI                                                                                       | High-performance async API framework, auto-generates OpenAPI docs, native Python type hints               |
| **User Interface**         | Vue.js 3 SPA (with Vite & Tailwind CSS)                                                       | Modern, reactive Single Page Application; built with Tailwind and PrimeVue for premium UI visual design.   |
| **Message Broker**         | Apache Kafka (or RabbitMQ)                                                                    | Event Bus for inter-service communication (as shown in the architecture diagram)                          |
| **Vector Database**        | FAISS (Facebook AI Similarity Search) or Qdrant                                               | Stores document embeddings for semantic search and similarity-based fusion                                |
| **Knowledge Graph**        | Neo4j                                                                                         | Stores structured relationships between knowledge entities; supports Cypher queries                       |
| **Relational Database**    | PostgreSQL                                                                                    | Centralized knowledge base for metadata, audit logs, and structured data                                  |
| **AI/ML Libraries**        | HuggingFace Transformers, Sentence-Transformers, scikit-learn, Prophet/statsmodels            | Embeddings (BERT/MiniLM), NER, clustering, time-series forecasting                                       |
| **LLM Integration**        | Google Gemini API (or OpenAI API)                                                             | RAG-based report generation, NLG, consistency checking via prompting                                      |
| **Containerization**       | Docker + Docker Compose                                                                       | Cloud Native microservices deployment; each task = one microservice container                              |
| **Service Registry**       | Consul (as shown in architecture diagram)                                                     | Service discovery for microservices                                                                       |
| **Monitoring & Logging**   | ELK Stack (Elasticsearch, Logstash, Kibana) + Prometheus                                      | As shown in architecture diagram; operational monitoring                                                  |
| **CI/CD**                  | GitHub Actions (or GitLab CI)                                                                 | Automated testing and deployment pipeline                                                                 |

## 0.5 Cloud Native Architecture

The architecture follows exactly the diagram provided by the supervisor (image copy 2.png) with the user interface implemented as a Vue.js 3 Web Application:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLOUD NATIVE — KM UPDATE SYSTEM                         │
│                                                                             │
│  ┌──────────┐    ┌──────────────────────────────────────────────────────┐   │
│  │ Sources  │    │           Event Bus / Message Broker                 │   │
│  │ Externes │◄──►│              (Kafka / RabbitMQ)                     │   │
│  │          │    └───┬──────┬──────┬──────┬──────┬──────────────────────┘   │
│  │ - Web/API│        │      │      │      │      │                         │
│  │ - Docs   │   ┌────▼──┐┌─▼────┐┌▼─────┐┌▼────┐┌▼──────┐                │
│  │ - Logs   │   │ T1:   ││ T2:  ││ T3:  ││ T4: ││ T5:   │                │
│  └──────────┘   │Prédic-││Rappor││Fusion││Cohé- ││Décou- │                │
│        │        │tion   ││ts    ││Intel.││rence ││verte  │                │
│  ┌─────▼─────┐  │       ││      ││      ││      ││       │                │
│  │API Gateway│  │ LSTM/ ││ LLM/ ││K-Means││NLP/ ││NER/   │                │
│  │ Entrée    │  │Prophet││ NLG  ││DBSCAN││Infer.││GNN    │                │
│  │ Unique    │  └───────┘└──────┘└──────┘└──────┘└───────┘                │
│  └─────┬─────┘                                                             │
│        │                                                                   │
│  ┌─────▼─────┐          ┌─────────────────────────┐                        │
│  │ Vue 3 Web │          │  Base de Connaissances   │                        │
│  │ Frontend  │◄────────►│  Centralisée             │                        │
│  │ (Port 5173│          │  ┌──────┐ ┌───────────┐  │    ┌─────────────────┐ │
│  └───────────┘          │  │Donnés│ │ Métadonnées│  │    │ Service Registry│ │
│                         │  │de Réf│ │            │  │    │ (Consul)        │ │
│                         │  └──────┘ └───────────┘  │    ├─────────────────┤ │
│                         └─────────────────────────┘    │ Monitoring &    │ │
│                                                        │ Logging (ELK,   │ │
│                         ┌─────────────────────────┐    │ Prometheus)     │ │
│                         │  Webhook Integrations   │    ├─────────────────┤ │
│                         │  (Slack / MS Teams)     │    │ CI/CD Pipeline  │ │
│                         └─────────────────────────┘    └─────────────────┘ │
│                                                                             │
│                    ──────────────────► Rapports de MàJ / Utilisateurs      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.5.1 Data Flow (Based on Architecture Diagram)

1. **External knowledge sources** (Web/API, Data Streams, Documents/Logs) enter through the **API Gateway** (single entry point).
2. The API Gateway publishes events to the **Event Bus** (Kafka/RabbitMQ).
3. **Task 1 (Prediction)** receives "Change Signals" and external data; uses supervised learning / anomaly detection to assess update needs.
4. **Task 5 (Discovery)** receives raw new knowledge; uses Text Mining / NER to extract entities and relationships.
5. **Task 3 (Fusion)** receives new raw knowledge; uses entity resolution / data fusion to merge with existing knowledge.
6. **Task 4 (Consistency)** receives fused knowledge; uses logical reasoning / ontological verification to validate.
7. **Task 2 (Report Generation)** receives validation logs and produces update reports using NLG / LLM.
8. All validated changes are written to the **Centralized Knowledge Base** (reference data + metadata).
9. The **Vue 3 Web Frontend** serves as the primary workspace for displaying dashboards, editing fused files, confirming consistency overrides, and reading reports. Optional **Webhook Integrations** can receive automated alerts for high-priority incidents.

## 0.6 Interoperability Dimension

The thesis proposal specifically identifies the gap in interoperability. Our system addresses this through:
- **REST APIs** (FastAPI with OpenAPI/Swagger) for integration with existing enterprise information systems.
- **Webhook mechanisms** for push-based notifications to external systems (including mapping to custom corporate communication channels like Slack or Microsoft Teams).
- **Standardized data formats** (JSON-LD, potentially RDF) for knowledge exchange.
- **Unified Vue Web Client** which acts as the direct management bridge between administrators and the system.

## 0.7 Development Timeline (4 Weeks)

| Week | Phase                                                  | Focus                                                             |
|------|--------------------------------------------------------|-------------------------------------------------------------------|
| 1    | Foundation & Data Engineering                          | Project setup, Docker, databases, data ingestion pipeline         |
| 2    | AI Core — The 5 Tasks                                  | Implement T1–T5 as individual microservices                       |
| 3    | Vue Frontend & AI Orchestration                        | Build Vue 3 Dashboard, RAG chat widget, alerts drawer, Orchestrator|
| 4    | Interoperability, Cloud Deployment & Evaluation        | External APIs, deploy to cloud, testing, thesis documentation     |

## 0.8 Validation Strategy

Following the approach established by prior Master projects, the system will be validated against:
- **Enterprise case study**: The OSS department of Mobilis (same as Ikram's memoir).
- **Synthetic datasets**: Created to simulate organizational knowledge documents (reports, procedures, technical manuals).
- **AI quality metrics**: ROUGE/BERTScore for summaries, Silhouette Score for clustering, F1 for NER, MAE/RMSE for time-series prediction.
