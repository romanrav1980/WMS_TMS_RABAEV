"""Publisher-only preview/import from named curated wiki sources."""
from typing import Any, Annotated
from fastapi import APIRouter, Depends
from pydantic import Field, StringConstraints
from .metadata_inputs import Input, Identifier, Reason
from .metadata_routes import MetadataUser, metadata_user
from ..contracts import KnowledgePublicationPort

wiki_publication_router = APIRouter(prefix="/api/knowledge/wiki-sources",tags=["wiki-publication"])
def wiki_publication_service() -> KnowledgePublicationPort:
    raise RuntimeError("Wiki publication service not composed")
class WikiImport(Input):
    operation_id: Annotated[str,StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")]
    source_id: Identifier
    source_revision: Annotated[str,StringConstraints(pattern=r"^[a-f0-9]{64}$")]
    expected_version: int = Field(strict=True,ge=0)
    reason: Reason
@wiki_publication_router.get("")
def wiki_sources(user: MetadataUser = Depends(metadata_user),service: KnowledgePublicationPort = Depends(wiki_publication_service)) -> list[dict[str,Any]]:
    return service.sources(user.username)
@wiki_publication_router.get("/{source_id}/preview")
def wiki_preview(source_id: str,user: MetadataUser = Depends(metadata_user),service: KnowledgePublicationPort = Depends(wiki_publication_service)) -> dict[str,Any]:
    return service.preview(user.username,source_id)
@wiki_publication_router.post("/import")
def wiki_import(body: WikiImport,user: MetadataUser = Depends(metadata_user),service: KnowledgePublicationPort = Depends(wiki_publication_service)) -> dict[str,Any]:
    return service.import_draft(user.username,body.model_dump())
