# 3. Week 3 — Slack Integration & AI Orchestration

> **Goal**: Connect the AI backend to users via the Slack chatbot interface and build the 5th sub-process (AI Orchestration) that autonomously manages the knowledge updating lifecycle.

---

## Day 1 (Mon): Slack App Configuration & Basic Bot Setup

### 3.1.1 Why Slack?

From the previous memoir (Ikram's work), Slack was identified as one of the key platforms for KM in enterprises (Table 1.5 in Chapter 1):

> **Slack** — Propriétaire, Gratuit — Features: Direct messaging, File attachments, Video/audio clips, Public/private channels.

The memoir also specifically lists Slack as a tool for "Soutien entre pairs" (Peer Support) in Table 2.1, making it the natural interface for our KM chatbot.

### 3.1.2 Slack App Setup

**Step 1: Create the Slack App**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From Manifest"
3. Use the following manifest:

```yaml
display_information:
  name: KM Update Bot
  description: AI-powered Knowledge Management Update System
  background_color: "#1a73e8"

features:
  bot_user:
    display_name: KM Bot
    always_online: true
  slash_commands:
    - command: /km-search
      url: https://<YOUR_DOMAIN>/slack/commands
      description: Search the knowledge base
      usage_hint: "[query]"
    - command: /km-status
      url: https://<YOUR_DOMAIN>/slack/commands
      description: Get KM system health status
    - command: /km-report
      url: https://<YOUR_DOMAIN>/slack/commands
      description: Generate an on-demand KM report
    - command: /km-predict
      url: https://<YOUR_DOMAIN>/slack/commands
      description: Check obsolescence score for a document
      usage_hint: "[document name or ID]"

oauth_config:
  scopes:
    bot:
      - chat:write
      - chat:write.public
      - commands
      - app_mentions:read
      - channels:history
      - channels:read
      - files:read
      - files:write
      - users:read

settings:
  event_subscriptions:
    request_url: https://<YOUR_DOMAIN>/slack/events
    bot_events:
      - app_mention
      - message.channels
  interactivity:
    is_enabled: true
    request_url: https://<YOUR_DOMAIN>/slack/interactions
```

**Step 2: Install to Workspace & Get Tokens**
- `SLACK_BOT_TOKEN` (xoxb-...)
- `SLACK_SIGNING_SECRET`
- `SLACK_APP_TOKEN` (for Socket Mode if using local development)

### 3.1.3 Basic Bot Server

```python
# services/slack-bot/app/main.py
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request

# Initialize Slack Bolt app
slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

# Initialize FastAPI
api = FastAPI(title="KM Slack Bot")
handler = SlackRequestHandler(slack_app)

@api.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)

@api.post("/slack/commands")
async def slack_commands(req: Request):
    return await handler.handle(req)

@api.post("/slack/interactions")
async def slack_interactions(req: Request):
    return await handler.handle(req)
```

### 3.1.4 Basic Slash Commands

```python
# services/slack-bot/app/handlers/commands.py

@slack_app.command("/km-status")
def handle_km_status(ack, respond):
    ack()
    # Query system health from all microservices
    metrics = get_dashboard_metrics()
    respond(
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 KM System Status"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Documents:* {metrics['total_documents']}"},
                    {"type": "mrkdwn", "text": f"*High Risk Docs:* {metrics['high_risk_count']}"},
                    {"type": "mrkdwn", "text": f"*Open Issues:* {metrics['consistency_issues_open']}"},
                    {"type": "mrkdwn", "text": f"*Fusions This Week:* {metrics['fusions_this_week']}"},
                ]
            }
        ]
    )
```

**Deliverable**: Slack bot responds to basic slash commands.

---

## Day 2 (Tue): RAG Pipeline — Intelligent Question Answering

### 3.2.1 RAG Architecture

This implements the "Assistant conversationnel IA pour l'enrichissement (KM Chatbot)" from Section 1.4.2, using **RAG + contextual memory**.

```
User asks question in Slack (@KM Bot what is our data backup policy?)
    ↓
1. Embed the user's query using Sentence-Transformer
    ↓
2. Search FAISS vector store for top-K similar knowledge chunks
    ↓
3. Build prompt: System instruction + Retrieved chunks + User question
    ↓
4. Send to LLM (Gemini API) for answer generation
    ↓
5. Format response with citations and post to Slack
```

### 3.2.2 RAG Implementation

```python
# services/slack-bot/app/rag/pipeline.py
class RAGPipeline:
    def __init__(self):
        self.encoder = KnowledgeEncoder()
        self.vector_store = VectorStore.load("data/faiss_index")
        self.llm = genai.GenerativeModel('gemini-2.0-flash')

    def answer(self, question: str, top_k: int = 5) -> dict:
        # Step 1: Embed query
        query_embedding = self.encoder.encode([question])

        # Step 2: Retrieve relevant chunks
        results = self.vector_store.search(query_embedding, top_k=top_k)
        chunks = [get_chunk_content(r['id']) for r in results]

        # Step 3: Build RAG prompt
        context = "\n\n---\n\n".join([
            f"[Source: {c['document_title']}, Dept: {c['department']}]\n{c['content']}"
            for c in chunks
        ])

        prompt = f"""You are an AI Knowledge Management assistant for an enterprise.
Answer the user's question based ONLY on the following retrieved knowledge base documents.
If the information is not in the documents, say "I don't have this information in the knowledge base."
Always cite which source document you're drawing from.

## Retrieved Knowledge:
{context}

## User Question:
{question}

## Instructions:
- Be concise and accurate
- Cite sources using [Source: document name]
- If information conflicts between sources, flag it
- Answer in the same language as the question
"""
        response = self.llm.generate_content(prompt)

        return {
            "answer": response.text,
            "sources": [c['document_title'] for c in chunks],
            "confidence": results[0]['score'] if results else 0
        }
```

### 3.2.3 Slack Event Handler for Mentions

```python
# services/slack-bot/app/handlers/events.py

@slack_app.event("app_mention")
def handle_mention(event, say):
    """When a user @mentions the bot, run RAG pipeline."""
    question = event["text"].split(">", 1)[-1].strip()  # Remove <@BOT_ID>

    if not question:
        say("Please ask me a question! Example: `@KM Bot what is our data backup policy?`")
        return

    # Show typing indicator
    say("🔍 Searching the knowledge base...")

    # Run RAG
    result = rag_pipeline.answer(question)

    # Format Slack response with Block Kit
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": result["answer"]}
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📚 Sources: {', '.join(result['sources'])} | Confidence: {result['confidence']:.0%}"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👍 Helpful"},
                    "action_id": "feedback_helpful",
                    "value": question
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👎 Not Helpful"},
                    "action_id": "feedback_not_helpful",
                    "value": question
                }
            ]
        }
    ]
    say(blocks=blocks)
```

**Deliverable**: An intelligent Q&A chatbot that answers organizational questions using internal knowledge.

---

## Day 3 (Wed): Proactive Notifications & Interactive Workflows

### 3.3.1 Proactive Alerts from Task 1 (Prediction)

When T1 detects a document with high obsolescence risk, the Orchestrator triggers a Slack notification:

```python
# services/slack-bot/app/handlers/alerts.py

def send_obsolescence_alert(channel: str, doc: dict, score: float):
    """
    Posts an interactive alert to Slack when a document is flagged as obsolete.
    Includes action buttons for the responsible person to act on.
    """
    slack_client.chat_postMessage(
        channel=channel,
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "⚠️ Knowledge Obsolescence Alert"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Document:* {doc['title']}\n"
                        f"*Department:* {doc['department']}\n"
                        f"*Obsolescence Score:* `{score:.0%}`\n"
                        f"*Last Updated:* {doc['last_updated']}\n"
                        f"*Reason:* Access frequency has declined by 70% over the past 30 days."
                    )
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Review & Update"},
                        "style": "primary",
                        "action_id": "review_update",
                        "value": doc['id']
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🗄️ Archive"},
                        "action_id": "archive_document",
                        "value": doc['id']
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Dismiss"},
                        "action_id": "dismiss_alert",
                        "value": doc['id']
                    }
                ]
            }
        ]
    )
```

### 3.3.2 Interactive Action Handlers

```python
# services/slack-bot/app/handlers/actions.py

@slack_app.action("review_update")
def handle_review(ack, body, respond):
    ack()
    doc_id = body["actions"][0]["value"]
    user = body["user"]["real_name"]
    
    # Update document status in database
    mark_document_under_review(doc_id, reviewer=user)
    
    # Log to audit trail
    audit_log("review_initiated", service="slack-bot",
              details={"document_id": doc_id, "reviewer": user})
    
    respond(f"✅ Document assigned to *{user}* for review. Status updated to `under_review`.")

@slack_app.action("archive_document")
def handle_archive(ack, body, respond):
    ack()
    doc_id = body["actions"][0]["value"]
    user = body["user"]["real_name"]
    
    archive_document(doc_id)
    audit_log("document_archived", service="slack-bot",
              details={"document_id": doc_id, "archived_by": user})
    
    respond(f"🗄️ Document archived by *{user}*.")
```

### 3.3.3 Channels Strategy

| Channel          | Purpose                                            |
|------------------|----------------------------------------------------|
| `#km-updates`    | Weekly reports (from T2) posted here every Friday   |
| `#km-alerts`     | Real-time obsolescence and consistency alerts       |
| `#km-discovery`  | New relationship discoveries from T5                |
| `#km-general`    | Q&A via @KM Bot mentions                           |

**Deliverable**: A fully interactive Slack bot with proactive alerts and action buttons.

---

## Day 4 (Thu): AI Orchestration — The 5th Sub-Process

### 3.4.1 Theoretical Foundation

This is the **novel contribution** of the thesis (Section 1.4.3):

> "L'apport principal de notre proposition réside dans l'introduction d'un cinquième sous-processus: celui d'Automatisation et d'Orchestration par l'Intelligence Artificielle."

The Orchestrator is responsible for:
1. **Sequencing** the 4 other sub-processes automatically.
2. **Permanent monitoring** of the knowledge base.
3. **Automatic conflict resolution** via AI consensus.
4. **Traceability and governance** via Explainable AI (XAI).

### 3.4.2 Orchestrator Implementation

```python
# services/orchestrator/app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class KMOrchestrator:
    """
    The 5th sub-process: Automation & AI Orchestration.
    Runs as a background daemon that coordinates all KM update tasks.
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.kafka_producer = KafkaProducer()

    def start(self):
        # Schedule recurring jobs
        self.scheduler.add_job(
            self.daily_scan, 'cron', hour=2, minute=0,  # 2:00 AM daily
            id='daily_scan'
        )
        self.scheduler.add_job(
            self.weekly_report, 'cron', day_of_week='fri', hour=17,  # Friday 5 PM
            id='weekly_report'
        )
        self.scheduler.add_job(
            self.continuous_monitoring, 'interval', minutes=30,
            id='continuous_monitoring'
        )
        self.scheduler.start()

    async def daily_scan(self):
        """
        Daily orchestration cycle:
        1. Run T1 (Prediction) on all active documents
        2. Run T3 (Fusion) to check for new duplicates
        3. Run T4 (Consistency) on modified documents
        4. Run T5 (Discovery) on new documents from last 24h
        5. Run T2 (Report) to summarize findings
        """
        audit_log("daily_scan_started", service="orchestrator")

        # Step 1: Trigger prediction scan
        await self.kafka_producer.send("orchestrator.trigger", {
            "action": "scan_predictions",
            "target": "all_active_documents",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Step 2: Trigger fusion check
        await self.kafka_producer.send("orchestrator.trigger", {
            "action": "scan_duplicates",
            "target": "recent_documents",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Steps 3-5 follow similar pattern...
        audit_log("daily_scan_completed", service="orchestrator")

    async def continuous_monitoring(self):
        """
        Every 30 minutes:
        - Check for new high-risk documents (score > 0.8)
        - Send immediate alerts to Slack #km-alerts if found
        """
        high_risk = get_documents_above_threshold(0.8)
        for doc in high_risk:
            if not already_alerted(doc['id']):
                send_slack_alert("#km-alerts", doc)
                mark_as_alerted(doc['id'])
                audit_log("alert_sent", service="orchestrator",
                         details={"document_id": doc['id'], "score": doc['score']},
                         explanation=f"Document '{doc['title']}' exceeded obsolescence threshold (score={doc['score']:.2f}). Alert sent to #km-alerts.")
```

### 3.4.3 Conflict Resolution

```python
# services/orchestrator/app/conflict_resolver.py

class ConflictResolver:
    """
    When T4 detects contradictions, and automatic resolution is possible,
    the Orchestrator resolves them. Otherwise, it escalates to humans via Slack.
    """
    def resolve(self, issue: dict) -> str:
        # Strategy 1: If one chunk is much newer, prefer it
        chunk_a_age = get_chunk_age(issue['chunk_a_id'])
        chunk_b_age = get_chunk_age(issue['chunk_b_id'])

        if abs(chunk_a_age - chunk_b_age) > 180:  # > 6 months difference
            newer = 'a' if chunk_a_age < chunk_b_age else 'b'
            archive_older_chunk(issue[f'chunk_{"b" if newer == "a" else "a"}_id'])
            audit_log("conflict_auto_resolved", service="orchestrator",
                     explanation=f"Conflict resolved by preferring newer document (age difference: {abs(chunk_a_age - chunk_b_age)} days).")
            return "auto_resolved"

        # Strategy 2: If confidence is borderline, escalate to human
        if issue['confidence'] < 0.9:
            send_slack_for_review("#km-alerts", issue)
            return "escalated_to_human"

        # Strategy 3: Use LLM to determine which is more authoritative
        resolution = self.llm_arbitrate(issue)
        audit_log("conflict_llm_resolved", service="orchestrator",
                 explanation=resolution['explanation'])
        return "llm_resolved"
```

### 3.4.4 Explainable AI (XAI) — Audit Trail

Every action taken by the Orchestrator is logged with a human-readable explanation:

```python
# services/orchestrator/app/audit_log.py
def audit_log(action: str, service: str, details: dict = None, explanation: str = None):
    """
    Writes to the audit_log table in PostgreSQL.
    The 'explanation' field provides XAI traceability — why this decision was made.
    """
    db.execute(
        "INSERT INTO audit_log (action, service, details, explanation) VALUES (%s, %s, %s, %s)",
        (action, service, json.dumps(details), explanation)
    )
```

**Deliverable**: A fully autonomous orchestrator that manages the KM lifecycle with traceability.

---

## Day 5 (Fri): Automated Reporting via Slack

### 3.5.1 Weekly Report Posting

```python
# services/slack-bot/app/handlers/reports.py

def post_weekly_report(channel="#km-updates"):
    """
    Called by the Orchestrator every Friday at 5 PM.
    Generates and posts the weekly KM health report.
    """
    # Get report from T2
    report_data = get_weekly_metrics()
    report_md = report_generator.generate_weekly_report(report_data)

    # Post to Slack (split if > 3000 chars)
    slack_client.chat_postMessage(
        channel=channel,
        text=f"📋 *Weekly KM Update Report — {date.today().strftime('%B %d, %Y')}*",
        blocks=[
            {"type": "header", "text": {"type": "plain_text", "text": f"📋 Weekly KM Report — {date.today().strftime('%B %d, %Y')}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": report_md[:3000]}},
            {"type": "divider"},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "🤖 Auto-generated by KM Bot | Powered by AI Orchestration"}]}
        ]
    )
    # Store in database
    save_report(report_md, report_type="weekly", channel=channel)
```

### 3.5.2 On-Demand Reports via Slash Command

```python
@slack_app.command("/km-report")
def handle_report_command(ack, respond):
    ack()
    respond("⏳ Generating your report... This may take a moment.")
    
    report_data = get_current_metrics()
    report_md = report_generator.generate_weekly_report(report_data)
    
    respond(
        text="📋 On-Demand KM Report",
        blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": report_md[:3000]}}
        ]
    )
```

**Deliverable**: Automated and on-demand reporting through Slack.

---

## Weekend (Sat–Sun): Polish & End-to-End Testing

### Tasks:
1. **Add conversational memory**: Store last 5 interactions per user to enable follow-up questions in RAG.
2. **Error handling**: Ensure the bot gracefully handles LLM API failures, empty search results, etc.
3. **Full E2E test scenario**:
   - Ingest 3 new documents → Verify T5 extracts entities → T3 checks for duplicates → T4 runs consistency → T1 computes scores → T2 generates report → Bot posts to `#km-updates`
   - Ask the bot a question → Verify it answers correctly with citations
   - Trigger an obsolescence alert → Verify interactive buttons work

### Week 3 Exit Criteria:
- [ ] Slack bot is connected to workspace and responds to all 4 slash commands
- [ ] RAG pipeline returns accurate answers with source citations
- [ ] Proactive alerts appear in `#km-alerts` when documents exceed threshold
- [ ] Interactive buttons (Review/Archive/Dismiss) update the database
- [ ] Orchestrator runs daily scan and posts weekly reports
- [ ] All orchestrator actions are logged in audit_log with explanations
- [ ] Conflict resolution works for age-based auto-resolution
