from pathlib import Path
"""Install native metadata services using the existing identity authority."""
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from .oracle_gateway import OracleGateway
from .auth import AdminUser, get_current_admin
from .modules.platform.public import (access_router, knowledge_admin_router, metadata_user, access_service,
    knowledge_admin_service, AccessMetadataService, KnowledgeMetadataService, NativePublishedHelp,
    MetadataError, knowledge_service, wiki_publication_router, wiki_publication_service, WikiPublication)

def register_metadata(app: FastAPI) -> None:
    gateway = OracleGateway()
    access = AccessMetadataService(gateway)
    knowledge = KnowledgeMetadataService(gateway)
    def bound_help(user: AdminUser = Depends(get_current_admin)) -> NativePublishedHelp:
        return NativePublishedHelp(knowledge,user.username)
    async def handle_error(request: Request, error: MetadataError) -> JSONResponse:
        return JSONResponse(status_code=error.status,content={"detail":{"code":error.code,"message":error.code,"outcome_confirmed":error.confirmed}})
    publication = WikiPublication(gateway,Path(__file__).resolve().parents[3])
    app.include_router(wiki_publication_router)
    app.dependency_overrides[wiki_publication_service] = lambda: publication
    app.include_router(access_router)
    app.include_router(knowledge_admin_router)
    app.dependency_overrides[metadata_user] = get_current_admin
    app.dependency_overrides[access_service] = lambda: access
    app.dependency_overrides[knowledge_admin_service] = lambda: knowledge
    app.dependency_overrides[knowledge_service] = bound_help
    app.add_exception_handler(MetadataError,handle_error)
