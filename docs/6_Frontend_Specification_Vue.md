# 6. Frontend Specification (Vue.js 3 & Tailwind CSS)

This document is the official technical specification for the **Vue.js 3** Single Page Application (SPA) frontend of the **Cloud-Native Knowledge Management (KM) Update System**. It defines the architecture, design system, component hierarchy, state management, and API endpoints for all pages, providing a complete reference for frontend developers.

---

## 6.1 Technology Stack & Architectural Decision

The frontend is a lightweight, high-performance web client built on Vue 3 and styled with Tailwind CSS. It communicates with the backend services via the API Gateway.

| Core Layer | Technology | Specification / Configuration |
| :--- | :--- | :--- |
| **Framework** | Vue 3 | Composition API, `<script setup>` syntax, TypeScript |
| **Build Tool** | Vite | Hot Module Replacement (HMR), optimized production bundling |
| **Routing** | Vue Router | Single Page Application (SPA) HTML5 history routing |
| **State Store** | Pinia | Modular reactive store architecture for task variables and cache |
| **Styling** | Tailwind CSS | Utility-first styling framework with glassmorphism presets |
| **UI Components** | PrimeVue (or shadcn-vue) | Fully accessible, customizable components (dialogs, charts, tables) |
| **Data Fetching** | Axios + TanStack Query | Query caching, automatic polling, background retry |
| **Data Visualization** | Chart.js / D3.js | Interactive charts, 2D vector projections, Neo4j graphs |
| **Real-Time Feed** | EventSource (SSE) / WebSockets | Live ingestion updates and model training progress |
| **Rich Text Editor** | TipTap / Quill | WYSIWYG editor for knowledge document CRUD |

---

## 6.2 Design System & Visual Identity

The interface uses a **Modern Premium Dark/Light Mode** theme emphasizing high visual polish, readability, and responsiveness.

### 6.2.1 Color Palette (Tailwind Custom Colors)
- **Primary / Accent**: Indigo/Blue (`#4F46E5` to `#3B82F6`) — representing AI intelligence.
- **Secondary**: Slate (`#0F172A` in Dark, `#F8FAFC` in Light) — core neutral background.
- **Success / Valid**: Emerald (`#10B981`) — representing healthy system status, consistency, and updates.
- **Warning / Alert**: Amber (`#F59E0B`) — representing moderate obsolescence risk or conflicts.
- **Danger / Conflict**: Rose (`#F43F5E`) — representing critical contradictions and high-risk obsolescence.

### 6.2.2 Typography & Elements
- **Font**: Outfit or Inter (Google Fonts) — modern geometric sans-serif.
- **Glassmorphism Preset**: 
  ```css
  .glass-panel {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  ```
- **Animations**: CSS transitions (`transition-all duration-300 ease-in-out`), hover scale animations (`hover:scale-[1.02]`), and micro-interactions for buttons.

---

## 6.3 Codebase Directory Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/             # Logos, images, global CSS variables
│   ├── components/         # Reusable UI Components
│   │   ├── layout/         # NavBar, Sidebar, Footer, BreadCrumb
│   │   ├── common/         # Button, Modal, Card, Loader, StatusBadge
│   │   ├── graphs/         # ForceDirectedGraph.vue (Neo4j), ScatterPlot.vue (D3)
│   │   └── widgets/        # RAGChatbot.vue, NotificationBell.vue
│   ├── router/             # Vue Router index and route guards
│   ├── stores/             # Pinia Stores (auth, knowledge, metrics, tasks)
│   ├── services/           # Axios HTTP client instances and API endpoint wrappers
│   ├── composables/        # Custom Vue Composables (e.g. useSSE, useTheme)
│   ├── views/              # Page components corresponding to paths
│   │   ├── Dashboard.vue
│   │   ├── Prediction.vue
│   │   ├── Reports.vue
│   │   ├── Fusion.vue
│   │   ├── Consistency.vue
│   │   ├── Discovery.vue
│   │   ├── KnowledgeBase.vue
│   │   ├── Monitoring.vue
│   │   ├── Audit.vue
│   │   └── Settings.vue
│   ├── App.vue             # Main Application shell
│   └── main.js             # Vue app bootstrap code
├── tailwind.config.js       # Tailwind setup
├── vite.config.js           # Vite configuration
└── package.json             # NPM dependencies
```

---

## 6.4 Pinia State Management

Four central stores manage the app's state, preventing duplicate network calls.

### 6.4.1 `useAuthStore`
Tracks the current user session and permission scope.
```javascript
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    role: localStorage.getItem('role') || 'Reader', // Admin, Expert, Reader
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.role === 'Admin',
    isExpert: (state) => state.role === 'Expert' || state.role === 'Admin',
  },
  actions: {
    setSession(token, user, role) { ... },
    clearSession() { ... }
  }
});
```

### 6.4.2 `useKnowledgeStore`
Manages cached knowledge assets, selected clusters, and active search queries.
- Holds search filters (`department`, `status`, `tag`).
- Caches the current document list to allow instant client-side filtering.

### 6.4.3 `useTaskStore`
Tracks long-running asynchronous AI jobs (polling status or SSE).
- Stores jobs mapping: `jobId` ➔ `{ status: 'RUNNING'|'SUCCESS'|'FAILED', progress: 0-100, service: 'T1'|'T3'|'T4'|'T5' }`.

---

## 6.5 Page Layouts & Component Breakdown

### 6.5.1 Dashboard View (`/`)
Serves as the primary operational workspace.
- **Hero Banner**: Displays system status and rapid ingestion trigger.
- **KPI Metrics Cards**:
  - *T1 Card*: Number of documents at high obsolescence risk.
  - *T2 Card*: Count of generated reports this month.
  - *T3 Card*: Estimated duplicate documents detected.
  - *T4 Card*: Global consistency index score (0-100%).
  - *T5 Card*: Newly discovered candidate concepts.
- **Active Alerts List**: Shows live system warnings (red/orange badges) for conflicts or severe decay.
- **Activity Timeline**: Log of recent events published to Kafka (e.g., "T3 merged 2 duplicates").

### 6.5.2 T1: Obsolescence Prediction (`/prediction`)
Allows users to evaluate documents for currency.
- **Config Panel**: Choose domain/department, select forecasting model (LSTM, Prophet, ARIMA, or Ensemble), set score alert threshold (0-100), and upload access logs.
- **Prediction Curve Chart**: A Line chart (Chart.js) showing historical access frequency (blue solid line) and forecast curve (dashed orange line) with confidence bands.
- **Priority Grid**: Table of documents marked by priority level (`Critical`, `High`, `Normal`), detailing their predicted decay date. Clicking on a row opens a details modal.
- **Asset Detail Modal**: Individual document view displaying an NLP-generated recommendation (e.g., "Treats outdated 4G protocol; recommend updating to 5G").

### 6.5.3 T2: Auto-Reports (`/reports`)
Accesses LLM-generated summaries backed by FAISS vector store.
- **Generation Drawer**: Configure report type (Weekly, Obsolescence Alert, Consistency Audit), select knowledge departments, and trigger LLM generation.
- **Report Viewer**: Renders HTML/Markdown, featuring:
    - *Interactive Citations*: Tooltips indicating source document chunks in PostgreSQL.
    - *Confidence Metric Badge*: Displays the sbert similarity score of the RAG lookup.
    - *Diff Inspector*: Slide-by-slide comparison comparing the draft report to a previous archive.
- **Templates Modal**: Allows administrators to modify the Gemini API system instructions (Prompt) and set the temperature (recommended: `0.2` for factuality).

### 6.5.4 T3: Intelligent Fusion (`/fusion`)
Visualizes semantic overlap and handles merging.
- **UMAP Scatter Plot**: Interactively projects document embeddings using D3.js. Points indicate document entities; colors signify K-Means clusters; clicking an entity highlights its cluster neighbors.
- **Cluster Review Panel**: Displays the selected cluster's cohesion score and an LLM-suggested master title.
- **Side-by-Side Diff**: Highlights textual additions and omissions between redundant candidate sheets.
- **Merge Dialog**: A Rich Text Editor containing the LLM-synthesized draft document. The KM expert edits and submits, marking the redundant duplicates as `archived` and linking them to the new node.

### 6.5.5 T4: Consistency Analysis (`/consistency`)
Evaluates logical conflicts.
- **Consistency Score Gauge**: Jauge chart showing the health percentage of the repository.
- **Neo4j Graph Panel**: Visualizes Concept nodes and their links. Normal associations are shown in slate grey; logical contradictions are marked as bold red arrows (`CONTRADICTS`).
- **Conflict Resolver**: Lists contradiction pairs. Displays LLM remediation recommendations (e.g., "Option A: Retain Doc 1, Option B: Retain Doc 2, Option C: Edit details").

### 6.5.6 T5: Knowledge Discovery (`/discovery`)
Ingests raw streams to identify relationships.
- **Ingestion Portal**: Upload PDF/DOCX or input a web scraper RSS URL.
- **NER Highlight Screen**: Displays the input text with highlights indicating identified entities (red for Organizations, blue for Technologies, green for Procedures).
- **Association Rules Table**: Lists rules mined via Apriori/FP-Growth, with support, confidence, and lift values.
- **Link Prediction Network**: A D3 layout plotting proposed associations between existing concepts. Clicking "Approve" creates the edge in Neo4j.

### 6.5.7 Central Knowledge Base Catalog (`/knowledge-base`)
The central CRUD repository.
- **Semantic Search Header**: Custom search bar query matching Postgres text search and FAISS vector embeddings.
- **List / Graph Toggle**: View as a card list or as a Neo4j force-directed graph.
- **Rich Editor Component**: Integrating TipTap, featuring an "AI Autocomplete" button that calls the LLM to complete sections based on context.

### 6.5.8 Monitoring & Operation Dash (`/monitoring`)
Supervisor console mapping Python services (equivalent to Eureka + Zipkin + Spring Boot Admin).
- **Consul Health Matrix**: Indicator panels showing status (UP/DOWN/WARNING) for the API Gateway, T1-T5 Services, and Orchestrator.
- **Metrics Panel**: Real-time charts plotting CPU usage, RAM utilization, and response latency.
- **Waterfall Trace Viewer**: Displays request execution across services (like Zipkin).
- **ELK Logs Terminal**: Interactive stream of application logs.

### 6.5.9 Audit Trail & Governance (`/audit`)
Ensures model explainability (XAI).
- **Decision Ledger**: Audit table logging every autonomous decision (e.g. "Auto-merged doc A and B").
- **XAI Explanation Card**: Detailed view displaying features, confidence metrics, and reasoning logic.
- **Human Override Action**: A button allowing KM experts to revert AI changes.

---

## 6.6 API Endpoint Directory (FastAPI Gateway)

The Vue client queries endpoints routed through the API Gateway:

| Method | Endpoint | Source Service | Request/Response Payload |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/auth/login` | API Gateway | In: `{username, password}` ➔ Out: `{token, user, role}` |
| **GET** | `/api/v1/dashboard/stats` | Orchestrator | Out: `{total_docs, high_risk_count, issues, fusions}` |
| **POST** | `/api/v1/prediction/run` | T1 Service | In: `{domain, model, threshold}` ➔ Out: `{job_id}` |
| **GET** | `/api/v1/prediction/results/{job_id}` | T1 Service | Out: `{scores: [{doc_id, score, priority}], chart_data}` |
| **POST** | `/api/v1/reports/generate` | T2 Service | In: `{type, departments, prompt_template}` ➔ Out: `{report_id}` |
| **GET** | `/api/v1/reports/{id}` | T2 Service | Out: `{id, title, content_html, confidence, sources: []}` |
| **POST** | `/api/v1/fusion/analyze` | T3 Service | In: `{algo, similarity_threshold}` ➔ Out: `{job_id}` |
| **GET** | `/api/v1/fusion/results/{job_id}` | T3 Service | Out: `{clusters: [{id, cohesion, docs: []}], projection_2d}` |
| **POST** | `/api/v1/fusion/execute` | T3 Service | In: `{cluster_id, master_doc, archived_docs: []}` ➔ Out: `{status: 'success'}` |
| **GET** | `/api/v1/consistency/score` | T4 Service | Out: `{score_percent, issues_count}` |
| **GET** | `/api/v1/consistency/graph` | T4/Neo4j | Out: `{nodes: [{id, label}], links: [{source, target, type}]}` |
| **POST** | `/api/v1/consistency/resolve` | T4 Service | In: `{issue_id, resolution_choice, justification}` ➔ Out: `{status}` |
| **POST** | `/api/v1/discovery/ingest` | T5 Service | In: `FormData` (file/url) ➔ Out: `{job_id}` |
| **GET** | `/api/v1/discovery/results/{job_id}` | T5 Service | Out: `{ner_entities: [], association_rules: [], predicted_links: []}` |
| **GET** | `/api/v1/knowledge-base` | KnowledgeBase | Out: `{documents: [{id, title, last_updated, status, ai_badges: {}}]}` |
| **POST** | `/api/v1/knowledge-base` | KnowledgeBase | In: `{title, content, department, relations: []}` ➔ Out: `{id}` |
| **GET** | `/api/v1/monitoring/health` | Consul | Out: `{services: [{name, status, cpu, ram, response_time}]}` |
| **GET** | `/api/v1/audit/logs` | Orchestrator | Out: `[{timestamp, action, service, explanation, override_allowed}]` |
| **POST** | `/api/v1/audit/override/{id}` | Orchestrator | In: `{reason}` ➔ Out: `{status: 'reversed'}` |
