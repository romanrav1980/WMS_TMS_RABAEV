"""HTTP contracts; native repositories own authorization and transaction boundaries."""
from dataclasses import dataclass
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from .metadata_inputs import Command, Explain, Kind, GroupSave, normalize
from ..contracts import AccessMetadataPort, KnowledgeMetadataPort

@dataclass(frozen=True)
class MetadataUser:
    username: str
    user_group: str

def metadata_user() -> MetadataUser:
    raise RuntimeError("Metadata authentication not composed")
def access_service() -> AccessMetadataPort:
    raise RuntimeError("Access service not composed")
def knowledge_admin_service() -> KnowledgeMetadataPort:
    raise RuntimeError("Knowledge administration not composed")

access_router = APIRouter(prefix="/api/access",tags=["scoped-access"])
knowledge_admin_router = APIRouter(prefix="/api/knowledge",tags=["knowledge-authoring"])

@access_router.get("/me")
def access_me(user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.me(user.username,user.user_group)
@access_router.get("/navigation")
def access_navigation(user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.navigation(user.username)

@access_router.get("/workspaces")
def access_workspaces(user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.workspaces(user.username)
@access_router.get("/catalog")
def access_catalog(user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.catalog(user.username)
@access_router.get("/groups")
def access_groups(query: str = Query(default="",max_length=120),limit: int = Query(default=50,ge=1,le=100),user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> list[dict[str,Any]]:
    return service.groups(user.username,query,limit)
@access_router.post("/groups/preview")
def access_group_preview(body: GroupSave,user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.preview_group(user.username,body.model_dump())
@access_router.get("/groups/{group_id}")
def access_group(group_id: str,user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.group(user.username,group_id)
@access_router.get("/objects")
def access_objects(kind: Kind,query: str = Query(default="",max_length=120),limit: int = Query(default=50,ge=1,le=100),user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> list[dict[str,Any]]:
    return service.objects(user.username,kind,query,limit)
@access_router.get("/assignments")
def access_assignments(username: str | None = Query(default=None,max_length=50),limit: int = Query(default=50,ge=1,le=100),user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> list[dict[str,Any]]:
    return service.assignments(user.username,username,limit)
@access_router.post("/explain")
def access_explain(body: Explain,user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.explain(user.username,body.username or user.username,body.permission,body.object_kind,body.object_id)

def validated(body: Command, domain: str) -> dict[str,Any]:
    try: return normalize(body,domain)
    except (ValidationError,ValueError) as error: raise HTTPException(422,{"code":"INVALID_COMMAND","message":str(error),"outcome_confirmed":True}) from error

@access_router.post("/commands")
def access_command(body: Command,user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.command(user.username,validated(body,"ACCESS"))
@access_router.get("/commands/{operation_id}")
def access_receipt(operation_id: str,user: MetadataUser = Depends(metadata_user), service: AccessMetadataPort = Depends(access_service)) -> dict[str,Any]:
    return service.receipt(user.username,operation_id)

@knowledge_admin_router.get("/spaces")
def knowledge_spaces(user: MetadataUser = Depends(metadata_user), service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> list[dict[str,Any]]:
    return service.spaces(user.username)
@knowledge_admin_router.get("/articles")
def knowledge_articles(space_id: str | None = Query(default=None,max_length=80),query: str = Query(default="",max_length=120),status: str | None = Query(default=None,pattern="^(DRAFT|PUBLISHED|ARCHIVED)$"),limit: int = Query(default=50,ge=1,le=100),user: MetadataUser = Depends(metadata_user),service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> list[dict[str,Any]]:
    return service.articles(user.username,space_id,query,status,limit)
@knowledge_admin_router.get("/articles/{article_id}")
def knowledge_article(article_id: str,user: MetadataUser = Depends(metadata_user), service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> dict[str,Any]:
    return service.article(user.username,article_id)
@knowledge_admin_router.get("/articles/{article_id}/history")
def knowledge_history(article_id: str,limit: int = Query(default=20,ge=1,le=50),user: MetadataUser = Depends(metadata_user), service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> list[dict[str,Any]]:
    return service.history(user.username,article_id,limit)
@knowledge_admin_router.post("/commands")
def knowledge_command(body: Command,user: MetadataUser = Depends(metadata_user), service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> dict[str,Any]:
    return service.command(user.username,validated(body,"KNOWLEDGE"))
@knowledge_admin_router.get("/commands/{operation_id}")
def knowledge_receipt(operation_id: str,user: MetadataUser = Depends(metadata_user), service: KnowledgeMetadataPort = Depends(knowledge_admin_service)) -> dict[str,Any]:
    return service.receipt(user.username,operation_id)
