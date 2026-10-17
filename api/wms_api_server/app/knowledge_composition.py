"""Composition for curated read-only help; existing identity authority is preserved."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .modules.platform.public import (KnowledgeService, PublishedKnowledge, knowledge_router,
                                      knowledge_service, knowledge_user, get_current_user)

def register_knowledge(app: FastAPI) -> None:
    # Only curated operator HTML lives here; never mount the project wiki or reports.
    help_path = Path(__file__).resolve().parents[3] / "docs" / "help" / "public"
    app.mount("/help", StaticFiles(directory=help_path, html=True), name="operator-help")
    catalog_path = Path(__file__).resolve().parents[3] / "docs" / "help" / "published.json"
    service = KnowledgeService(PublishedKnowledge(catalog_path))
    app.include_router(knowledge_router)
    app.dependency_overrides[knowledge_service] = lambda: service
    app.dependency_overrides[knowledge_user] = get_current_user
