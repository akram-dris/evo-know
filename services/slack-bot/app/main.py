from fastapi import FastAPI

api = FastAPI(
    title="KM Slack Bot Interface",
    description="Slack Bot backend and RAG conversational interface.",
    version="1.0.0"
)

@api.get("/health")
async def health_check():
    return {"status": "online", "service": "slack-bot"}

@api.get("/")
async def root():
    return {"service": "slack-bot", "status": "operational"}
