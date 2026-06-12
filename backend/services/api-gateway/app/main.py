from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, ingest, query, alerts, audit, reports, external_api, auth_routes, dashboard, tasks_api

app = FastAPI(
    title="KM API Gateway",
    description="Single entry point for the Cloud Native Knowledge Management Update System.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(alerts.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(external_api.router)
app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(tasks_api.router)

@app.get("/")
async def root():
    return {
        "service": "api-gateway",
        "status": "operational",
        "documentation": "/docs"
    }
