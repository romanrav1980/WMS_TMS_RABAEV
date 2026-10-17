"""Authenticated, bounded access to prepared help; no command or wiki filesystem API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from dataclasses import dataclass
from ..application.knowledge import KnowledgeService

@dataclass(frozen=True)
class KnowledgeUser:
    permissions: set[str]

def knowledge_user() -> KnowledgeUser:
    raise RuntimeError("Knowledge authentication not composed")

knowledge_router = APIRouter(prefix="/api/help", tags=["published-knowledge"])

def knowledge_service() -> KnowledgeService:
    raise RuntimeError("Knowledge service not composed")

@knowledge_router.get("/articles")
def search_articles(query: str = Query(default="", max_length=120), limit: int = Query(default=20, ge=1, le=50),
                    user: KnowledgeUser = Depends(knowledge_user),
                    service: KnowledgeService = Depends(knowledge_service)) -> list[dict[str, str]]:
    return service.search(query, user.permissions, limit)

@knowledge_router.get("/articles/{article_id}")
def read_article(article_id: str, user: KnowledgeUser = Depends(knowledge_user),
                 service: KnowledgeService = Depends(knowledge_service)) -> dict[str, object]:
    article = service.detail(article_id, user.permissions)
    if article is None:
        raise HTTPException(404, "Статья недоступна или не опубликована")
    return article
