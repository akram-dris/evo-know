# 🧪 Verification Tests for EvoKnow System (Weeks 1-3)

This document provides a consolidated list of verification commands for each week's deliverables, including both Linux (`curl`) and Windows (`curl.exe`) versions, along with expected outputs or behaviors. This serves as a quick reference for end-to-end testing and validation.

---

## 🚀 Week 1: Foundation, Architecture & Data Engineering

### 🟢 Test 1: API Health & Database Connectivity

*   **Description:** Verify that the API Gateway is operational and connected to PostgreSQL and Neo4j.
*   **Linux (Bash):**
    ```bash
    curl -i http://127.0.0.1:8000/health
    ```
*   **Windows (CMD/PowerShell):**
    ```cmd
    curl.exe -i http://127.0.0.1:8000/health
    ```
*   **Expected Output (HTTP 200 OK):**
    ```json
    {
      "status": "online",
      "service": "api-gateway",
      "database": "healthy"
    }
    ```

### 🟢 Test 2: Knowledge Ingestion Pipeline

*   **Description:** Upload a sample knowledge document to trigger the ingestion pipeline. This validates parsing, chunking, embedding, and storage.
*   **Linux (Bash):**
    ```bash
    curl -X POST -F "file=@backend/sample_knowledge.txt" -F "department=AI Research" -F "uploaded_by=TestUser" http://127.0.0.1:8000/ingest
    ```
*   **Windows (CMD/PowerShell):**
    ```cmd
    curl.exe -X POST -F "file=@backend/sample_knowledge.txt" -F "department=AI Research" -F "uploaded_by=TestUser" http://127.0.0.1:8000/ingest
    ```
*   **Expected Output (HTTP 200 OK):**
    ```json
    {
      "status": "success",
      "document_id": "...",
      "chunks_created": "...",
      "message": "Document successfully ingested, embedded, and indexed."
    }
    ```
    *(Note: `document_id` and `chunks_created` will vary.)*

### 🟢 Test 3: Semantic Search & Retrieval

*   **Description:** Submit a natural language query to retrieve relevant knowledge chunks.
*   **Linux (Bash):**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"question": "What is the role of Apache Kafka in the system?", "top_k": 2}' http://127.0.0.1:8000/query
    ```
*   **Windows (CMD/PowerShell):**
    ```cmd
    curl.exe -X POST -H "Content-Type: application/json" -d '{"question": "What is the role of Apache Kafka in the system?", "top_k": 2}' http://127.0.0.1:8000/query
    ```
*   **Expected Behavior:** Returns relevant chunks related to Kafka.
    *(Note: The exact JSON output will depend on the ingested data.)*

---

## 🚀 Week 2: AI Core Microservices Deployment & Verification

*(Note: Most Week 2 tests involve observing Kafka events and audit logs, which are harder to test directly via `curl`. Manual inspection of Docker container logs or the UI's Audit Log view (Week 3) is recommended.)*

### 🟢 Test 1: Ingestion Pipeline Triggered by Operator

*   **Description:** Ingest a document, attributing it to an operator (e.g., Asma).
*   **Linux (Bash):**
    ```bash
    curl -X POST -F "file=@backend/sample_knowledge.txt" -F "department=AI Research" -F "uploaded_by=Asma" http://127.0.0.1:8000/ingest
    ```
*   **Windows (CMD/PowerShell):**
    ```cmd
    curl.exe -X POST -F "file=@backend/sample_knowledge.txt" -F "department=AI Research" -F "uploaded_by=Asma" http://127.0.0.1:8000/ingest
    ```
*   **Expected Output (HTTP 200 OK):**
    ```json
    {
      "status": "success",
      "document_id": "...",
      "chunks_created": "...",
      "message": "Document successfully ingested, embedded, and indexed."
    }
    ```
    *Verification:* Check `orchestrator` container logs for messages indicating processing of `document.ingested` event.

### 🟢 Test 2: Verify AI Microservices Processing

*   **Description:** After ingestion, observe the orchestrator logs and potentially audit logs (via Week 3 UI) to confirm T1-T5 services process the event chain.
*   **Linux (Bash):**
    ```bash
    docker compose logs orchestrator
    ```
*   **Windows (CMD/PowerShell):**
    ```cmd
    docker compose logs orchestrator
    ```
*   **Expected Behavior:** Logs should show the orchestrator processing various Kafka events (`document.ingested`, `discovery.found`, `fusion.completed`, `consistency.checked`, `prediction.scored`, `report.generated`) and logging audit entries.

---

## 🚀 Week 3: Vue Frontend Integration & AI Orchestration

### 🟢 Test 1: RAG Chatbot Functionality (UI)

*   **Description:** Interact with the RAG chatbot in the Vue frontend.
*   **Steps:**
    1.  Open your web browser and navigate to `http://localhost:5173/`.
    2.  Click on "Base de connaissances" in the sidebar.
    3.  Type a question in the chatbot input field (e.g., "What is a microservice architecture?") and press Enter.
*   **Expected Behavior:** The chatbot should respond with an AI-generated answer, displaying sources and a confidence score.

### 🟢 Test 2: Real-time Alerts Stream (UI)

*   **Description:** Observe dynamic alerts appearing in the frontend.
*   **Steps:**
    1.  Open your web browser and navigate to `http://localhost:5173/`.
    2.  (Optional) If you have a Kafka producer setup, send a test message to the `orchestrator.alert` topic (e.g., `{"id": "test-123", "title": "Test Alert", "message": "This is a test notification.", "severity": "warning", "timestamp": "2026-06-07T10:00:00Z"}`).
*   **Expected Behavior:** An `AlertCard` should slide into view in the bottom-right corner of the application with the alert details.

### 🟢 Test 3: Audit Log Display (UI)

*   **Description:** Verify that the audit logs from the orchestrator are displayed in the UI.
*   **Steps:**
    1.  Open your web browser and navigate to `http://localhost:5173/`.
    2.  Click on "Registre d'audit (XAI)" in the sidebar.
*   **Expected Behavior:** A table should display a list of audit logs generated by the `KMOrchestrator`, including actions, system components, and XAI explanations.

### 🟢 Test 4: Auto-Generated Reports Display (UI)

*   **Description:** Access and view the auto-generated reports.
*   **Steps:**
    1.  Open your web browser and navigate to `http://localhost:5173/`.
    2.  Click on "T2 : Rapports" in the sidebar.
*   **Expected Behavior:** A list of historical reports should appear on the left. Clicking on a report should display its Markdown content (rendered as HTML) on the right side of the screen.
---
