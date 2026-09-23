import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.database import init_db
from app.rag.ingestion import ingest_knowledge_base
from app.api import tickets, workflows, approvals, agents, logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    await init_db()
    # Ingest Knowledge Base documents into ChromaDB on startup if available
    kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
    if not os.path.exists(kb_path):
        kb_path = os.path.abspath("./knowledge_base")
    ingest_knowledge_base(kb_path)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AgentFlow — Multi-Agent Business Workflow Automation System API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(tickets.router, prefix=settings.API_V1_STR)
app.include_router(workflows.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(logs.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AgentFlow Backend", "version": settings.VERSION}

@app.get("/ready")
def readiness_check():
    return {"status": "ready", "llm_provider": settings.LLM_PROVIDER}

# Prometheus metrics endpoint
if settings.PROMETHEUS_METRICS_ENABLED:
    try:
        from prometheus_client import make_asgi_app
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    except Exception:
        pass
