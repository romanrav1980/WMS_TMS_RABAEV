"""Explicit abandonment and read-only resolution; original receipts keep their contract."""
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_resource_intents import (ResourceIntentAbandon, ResourceIntentError,
    ResourceIntentPort, ResourceIntentQuery, resource_intent_service)

router = APIRouter(prefix="/api/resources/metadata-intents", tags=["resource-intent-recovery"])


def failure(error: ResourceIntentError) -> HTTPException:
    return HTTPException(error.status, dict(code=error.code, operation_id=error.operation_id,
        outcome_confirmed=False, read_before_retry=True))


@router.post("/abandonments")
def abandon(body: ResourceIntentAbandon, user: AdminUser = Depends(get_current_user),
            service: ResourceIntentPort = Depends(resource_intent_service)) -> dict[str, Any]:
    try:
        return service.abandon(body, user.username)
    except ResourceIntentError as error:
        raise failure(error) from error


@router.get("/abandonments/{operation_id}")
def receipt(operation_id: str, user: AdminUser = Depends(get_current_user),
            service: ResourceIntentPort = Depends(resource_intent_service)) -> dict[str, Any]:
    try:
        return service.receipt(operation_id, user.username)
    except ResourceIntentError as error:
        raise failure(error) from error


@router.get("/resolution")
def resolution(domain: Literal["CASE", "TASK"], task_id: int = Query(gt=0),
               original_operation_id: str = Query(pattern=r"^[A-Za-z0-9_.:-]{1,100}$"),
               action: Literal["CLAIM", "ASSIGN", "START"] = Query(),
               target: str = Query(min_length=1, max_length=100),
               original_request_sha256: str = Query(pattern=r"^[A-F0-9]{64}$"),
               user: AdminUser = Depends(get_current_user),
               service: ResourceIntentPort = Depends(resource_intent_service)) -> dict[str, Any]:
    if action == ("ASSIGN" if domain == "CASE" else "CLAIM"):
        raise HTTPException(422, "Action belongs to another metadata domain")
    body = ResourceIntentQuery(domain=domain, task_id=task_id, original_operation_id=original_operation_id,
        action=action, target=target, original_request_sha256=original_request_sha256)
    try:
        return service.resolution(body, user.username)
    except ResourceIntentError as error:
        raise failure(error) from error

