import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.db.database import engine, Base, SessionLocal
from app.db.seed_data import seed_database
from app.api.routes_kb import router as kb_router
from app.api.routes_review import router as review_router
from app.api.routes_workflow import router as workflow_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_parser import router as parser_router

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

# Seed initial Brand Kit (Verity Brand Guidelines 2026, Facts, Assets)
with SessionLocal() as db:
    seed_database(db)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Pre-publication brand governance that cites its sources, explains every finding and keeps humans in charge."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(kb_router, prefix=settings.API_V1_PREFIX)
app.include_router(review_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflow_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
app.include_router(parser_router, prefix=settings.API_V1_PREFIX)

# Static Files & SPA Frontend
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Verity Brand Governance Engine",
        "version": settings.VERSION,
        "ai_disclosure": settings.AI_MODEL_DISCLOSURE,
        "confidentiality": settings.CONFIDENTIALITY_NOTICE
    }
