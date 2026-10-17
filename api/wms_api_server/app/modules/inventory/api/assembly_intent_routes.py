"""Explicit durable cancellation of attempts which never created native work."""
from typing import Any
from fastapi import APIRouter,Depends
from ...platform.public import AdminUser,get_current_user
from ..contracts_assembly_scale import AssemblyScaleError
from ..contracts_assembly_intents import AbandonIntent,AssemblyIntentPort,assembly_intent_service
from .assembly_scale_routes import failure
router=APIRouter(prefix="/api/inventory/assembly-scale/abandonments",tags=["assembly-intents"])

@router.post("")
def abandon(body: AbandonIntent,user: AdminUser=Depends(get_current_user),
            service: AssemblyIntentPort=Depends(assembly_intent_service)) -> dict[str,Any]:
    try:
        return service.abandon(body,user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc

@router.get("/{identity}")
def read(identity: str,user: AdminUser=Depends(get_current_user),
         service: AssemblyIntentPort=Depends(assembly_intent_service)) -> dict[str,Any]:
    try:
        return service.read(identity,user.username)
    except AssemblyScaleError as exc:
        raise failure(exc) from exc
