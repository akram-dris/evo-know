# 3. Week 3 — Vue 3 Frontend Integration & AI Orchestration

> **Goal**: Connect the AI backend services to users via the Vue.js 3 Web Application and implement the 5th sub-process (AI Orchestration) that autonomously manages the knowledge updating lifecycle.

---

## Day 1 (Mon): Vue 3 Project Setup & Global Shell Layout

### 3.1.1 Vue 3 + Tailwind CSS Stack Setup
Initialize a clean Vue 3 application with Vite, Pinia, Vue Router, and Tailwind CSS.
```bash
# Create Vue 3 application
npx -y create-vite@latest frontend --template vue-ts
cd frontend
npm install

# Install Tailwind CSS and components library
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install core client libraries
npm install pinia vue-router axios @tanstack/vue-query lucide-vue-next primevue
```

### 3.1.2 Global Layout & Shell Components
The main interface uses a grid shell with a sticky sidebar, header navigation, and content view.

```vue
<!-- frontend/src/components/layout/Shell.vue -->
<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 flex font-sans">
    <!-- Sidebar Navigation -->
    <aside class="w-64 border-r border-slate-800 bg-slate-950 flex flex-col p-4 space-y-6">
      <div class="flex items-center space-x-2 px-2 py-3">
        <div class="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
          <span class="font-bold text-white">KM</span>
        </div>
        <span class="font-bold text-xl tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">EvoKnow</span>
      </div>
      <nav class="flex-1 space-y-1">
        <router-link to="/" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <LayoutDashboardIcon class="h-5 w-5" />
          <span>Dashboard</span>
        </router-link>
        <router-link to="/prediction" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <TrendingUpIcon class="h-5 w-5" />
          <span>T1: Prediction</span>
        </router-link>
        <router-link to="/reports" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <FileTextIcon class="h-5 w-5" />
          <span>T2: Reports</span>
        </router-link>
        <router-link to="/fusion" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <GitMergeIcon class="h-5 w-5" />
          <span>T3: Fusion</span>
        </router-link>
        <router-link to="/consistency" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <ShieldAlertIcon class="h-5 w-5" />
          <span>T4: Consistency</span>
        </router-link>
        <router-link to="/discovery" class="nav-item flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-850 hover:text-white transition-all">
          <CpuIcon class="h-5 w-5" />
          <span>T5: Discovery</span>
        </router-link>
      </nav>
      <div class="border-t border-slate-800 pt-4">
        <router-link to="/audit" class="flex items-center space-x-3 px-3 py-2 rounded-lg text-slate-400 hover:text-white">
          <HistoryIcon class="h-4 w-4" />
          <span class="text-sm">Audit Trail (XAI)</span>
        </router-link>
      </div>
    </aside>

    <!-- Main Workspace -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Navbar / Top Header -->
      <header class="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-45">
        <div class="flex items-center space-x-4">
          <h2 class="font-semibold text-lg text-white">KM Update System</h2>
          <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-xs text-slate-400 font-mono">Consul: Connected</span>
        </div>
        <div class="flex items-center space-x-4">
          <NotificationBell />
          <UserMenu />
        </div>
      </header>

      <!-- Page Content View -->
      <main class="flex-1 p-6 overflow-y-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>
```

**Deliverable**: Vue 3 project structure initialized with Tailwind CSS styling and global layout.

---

## Day 2 (Tue): RAG Chatbot Integration in the Web UI

### 3.2.1 RAG API Route
Expose the semantic query capability directly to the Vue frontend via the API Gateway.
```python
# backend/services/api-gateway/app/routes/query.py
@router.post("/query")
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    1. Retrieve similarity vectors from FAISS.
    2. Retrieve raw source chunks from PostgreSQL.
    3. Generate contextual answer via Google Gemini API.
    4. Return formatted JSON response with citations.
    """
    results = search_vector_store(request.question)
    prompt = build_rag_prompt(request.question, results)
    answer = call_gemini_api(prompt)
    return {
        "answer": answer,
        "sources": [doc.title for doc in results],
        "confidence": compute_confidence_score(results)
    }
```

### 3.2.2 Vue RAG Chatbot Widget
Embed an interactive Q&A assistant inside the knowledge base view.

```vue
<!-- frontend/src/components/widgets/RAGChatbot.vue -->
<script setup>
import { ref } from 'vue';
import axios from 'axios';

const query = ref('');
const messages = ref([
  { sender: 'bot', text: 'Hello! Ask me anything about our enterprise knowledge repository.' }
]);
const loading = ref(false);

const sendMessage = async () => {
  if (!query.value.trim()) return;
  
  messages.value.push({ sender: 'user', text: query.value });
  const userQuery = query.value;
  query.value = '';
  loading.value = true;
  
  try {
    const res = await axios.post('/api/v1/query', { question: userQuery });
    messages.value.push({ 
      sender: 'bot', 
      text: res.data.answer,
      sources: res.data.sources,
      confidence: res.data.confidence
    });
  } catch (err) {
    messages.value.push({ sender: 'bot', text: 'Error contacting LLM API.' });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex flex-col h-[500px] bg-slate-950 border border-slate-800 rounded-xl overflow-hidden glass-panel">
    <div class="p-4 border-b border-slate-850 bg-slate-900/50 flex justify-between items-center">
      <h3 class="font-medium text-slate-200">AI Knowledge Assistant</h3>
      <span class="text-xs text-slate-400 font-mono">Gemini-2.0-Flash</span>
    </div>
    <!-- Message Feed -->
    <div class="flex-1 p-4 overflow-y-auto space-y-3">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['p-3 rounded-lg max-w-[85%] text-sm', msg.sender === 'user' ? 'bg-indigo-600 ml-auto' : 'bg-slate-850']">
        <p>{{ msg.text }}</p>
        <div v-if="msg.sources" class="mt-2 pt-2 border-t border-slate-800 text-xs text-slate-400">
          <span>Sources: {{ msg.sources.join(', ') }}</span>
          <span class="ml-2">| Confidence: {{ (msg.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div v-if="loading" class="text-slate-400 text-xs animate-pulse">Searching vector store & synthesizing answer...</div>
    </div>
    <!-- Input Box -->
    <div class="p-3 border-t border-slate-850 flex space-x-2">
      <input v-model="query" @keyup.enter="sendMessage" placeholder="Ask a question..." 
             class="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 text-sm focus:outline-none focus:border-indigo-500" />
      <button @click="sendMessage" class="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium">Send</button>
    </div>
  </div>
</template>
```

**Deliverable**: RAG widget embedded in the web interface for semantic Q&A with real-time confidence scores and citation references.

---

## Day 3 (Wed): Real-time Ingestion Metrics & Active Alerts

### 3.3.1 SSE Alerts Event Bus
Replace the interactive Slack alerts with a **Server-Sent Events (SSE)** endpoint in the API Gateway. The Vue client subscribes to this endpoint to receive push alerts.

```python
# backend/services/api-gateway/app/routes/alerts.py
from sse_starlette.sse import EventPublisher, EventSourceResponse

@router.get("/alerts/stream")
async def alerts_stream(request: Request):
    """
    Exposes an SSE channel publishing alerts pushed from Kafka topics
    ('prediction.scored', 'consistency.checked', etc.).
    """
    async def event_generator():
        async for msg in kafka_consumer.listen():
            if msg.topic == "orchestrator.alert":
                yield {
                    "event": "alert",
                    "data": json.dumps(msg.value)
                }
    return EventSourceResponse(event_generator())
```

### 3.3.2 Vue Real-Time Alert Card
A sliding active alert card displaying incoming warnings and immediate actions.

```vue
<!-- frontend/src/components/widgets/AlertCard.vue -->
<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  alert: Object
});
const emit = defineEmits(['resolve']);

const takeAction = async (action) => {
  emit('resolve', props.alert.id, action);
};
</script>

<template>
  <div class="p-4 border-l-4 rounded-r-lg flex items-start space-x-4 glass-panel"
       :class="alert.severity === 'critical' ? 'border-rose-500 bg-rose-500/5' : 'border-amber-500 bg-amber-500/5'">
    <div class="flex-1">
      <div class="flex items-center space-x-2">
        <span class="font-semibold text-sm">{{ alert.title }}</span>
        <span class="text-xs px-2 py-0.5 rounded" 
              :class="alert.severity === 'critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'">
          {{ alert.severity }}
        </span>
      </div>
      <p class="text-xs text-slate-400 mt-1">{{ alert.message }}</p>
      <div class="mt-3 flex space-x-2">
        <button @click="takeAction('review')" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-1.5 rounded font-medium">Review</button>
        <button @click="takeAction('archive')" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded font-medium">Archive</button>
      </div>
    </div>
  </div>
</template>
```

**Deliverable**: Real-time push alert network in the UI using Server-Sent Events.

---

## Day 4 (Thu): AI Orchestration (The 5th Sub-Process)

The Orchestrator coordinates T1-T5 microservices, writing decisions to the `audit_log` table with explainable AI fields.

```python
# backend/services/orchestrator/app/main.py
class KMOrchestrator:
    """
    Coordinates T1-T5, manages scheduler loop, handles conflict resolution,
    and writes XAI explanations to the postgres audit database.
    """
    def resolve_conflicts(self, conflict: dict):
        if conflict["age_diff_days"] > 180:
            # Auto-supersede older chunk
            archive_chunk(conflict["older_chunk_id"])
            log_xai_audit(
                action="auto_supersede",
                explanation=f"Superseded chunk {conflict['older_chunk_id']} with newer duplicate {conflict['newer_chunk_id']} (Age diff: {conflict['age_diff_days']} days)."
            )
        else:
            # Escalate to Vue frontend dashboard as an active alert
            raise_dashboard_alert(conflict)
```

The audit log is fetched and rendered in the Vue `/audit` view.

```vue
<!-- frontend/src/views/Audit.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-white">XAI Audit Ledger</h1>
      <span class="text-xs text-indigo-400 font-mono">Traceability and Compliance</span>
    </div>
    
    <div class="bg-slate-950 border border-slate-850 rounded-xl overflow-hidden glass-panel">
      <table class="w-full text-left border-collapse">
        <thead class="bg-slate-900/60 text-slate-400 text-xs font-semibold">
          <tr>
            <th class="p-4 border-b border-slate-850">Timestamp</th>
            <th class="p-4 border-b border-slate-850">Action</th>
            <th class="p-4 border-b border-slate-850">System Component</th>
            <th class="p-4 border-b border-slate-850">AI Explanation</th>
            <th class="p-4 border-b border-slate-850">Status</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-slate-850">
          <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-900/20">
            <td class="p-4 text-slate-400 font-mono text-xs">{{ formatDate(log.performed_at) }}</td>
            <td class="p-4 font-medium text-slate-200">{{ log.action }}</td>
            <td class="p-4"><span class="bg-indigo-950 text-indigo-300 text-xs px-2 py-0.5 rounded">{{ log.service }}</span></td>
            <td class="p-4 text-slate-300 italic">{{ log.explanation }}</td>
            <td class="p-4">
              <span class="text-xs text-emerald-400 font-semibold">Verified</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
```

**Deliverable**: Automated background orchestrator communicating with the Vue `/audit` page.

---

## Day 5 (Fri): Auto-Generated Reports View

Renders the automatic markdown reports from Task 2 (LLM-synthesized) inside the UI, and provides visual comparisons.

```vue
<!-- frontend/src/views/Reports.vue -->
<template>
  <div class="grid grid-cols-3 gap-6">
    <!-- Left Column: Report List -->
    <div class="col-span-1 bg-slate-950 border border-slate-850 rounded-xl p-4 space-y-4 glass-panel">
      <h3 class="font-semibold text-slate-200">Historical Reports</h3>
      <div class="space-y-2">
        <div v-for="rep in reports" :key="rep.id" @click="selectReport(rep)" 
             class="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500 cursor-pointer transition">
          <div class="flex justify-between text-xs text-slate-400">
            <span>{{ rep.type }}</span>
            <span>{{ formatDate(rep.generated_at) }}</span>
          </div>
          <p class="text-sm font-medium text-slate-200 mt-1">{{ rep.title }}</p>
        </div>
      </div>
    </div>
    
    <!-- Right Column: Document Viewer and Comparison -->
    <div class="col-span-2 bg-slate-950 border border-slate-850 rounded-xl p-6 glass-panel space-y-4">
      <div v-if="selectedReport" class="space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 class="text-xl font-bold text-slate-200">{{ selectedReport.title }}</h2>
          <div class="flex space-x-2">
            <button class="bg-indigo-600 text-xs px-3 py-1.5 rounded">Download PDF</button>
            <button class="bg-slate-800 text-xs px-3 py-1.5 rounded" @click="compareMode = !compareMode">Compare Versions</button>
          </div>
        </div>
        
        <div class="prose prose-invert max-w-none text-slate-350 text-sm leading-relaxed" v-html="selectedReport.content_html"></div>
      </div>
      <div v-else class="text-slate-400 text-center py-20">Select a report from the list to view its contents.</div>
    </div>
  </div>
</template>
```

---

## Weekend (Sat–Sun): Integration & End-to-End Local Running

### Test Scenario
1. Run database initialization and seed:
   ```bash
   docker compose up -d
   docker compose exec api-gateway python backend/scripts/init_databases.py
   ```
2. Upload `sample_knowledge.txt` via the Vue Document upload card.
3. Verify that the Kafka consumer logs capture events and update metrics on the dashboard.
4. Verify that the RAG widget retrieves knowledge pieces and returns answers.

### Week 3 Exit Criteria
- [ ] Vue 3 application builds and runs in development mode without script errors.
- [ ] Tailwind CSS configuration correctly applies themes and fonts.
- [ ] RAG Chat component responds to queries with accurate source citations.
- [ ] Alert drawers slide open upon receiving SSE signals.
- [ ] Orchestration logs map correctly to the Audit table.
- [ ] Markdown reports are compiled into HTML within the viewer panel.
