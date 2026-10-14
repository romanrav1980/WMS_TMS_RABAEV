"""Existing minimax lifecycle exposed through typed, composition-injected ports."""
from typing import Any,Protocol
from fastapi import APIRouter,Depends,Path
class MinimaxUser(Protocol):
    username: str
class MinimaxPort(Protocol):
    def preview(self,warehouse: int)->dict[str,Any]: ...
    def reconcile(self,warehouse: int,actor: str)->dict[str,Any]: ...
def minimax_view()->MinimaxUser:raise RuntimeError("Minimax view rights not wired")
def minimax_edit()->MinimaxUser:raise RuntimeError("Minimax execution rights not wired")
def minimax_service()->MinimaxPort:raise RuntimeError("Minimax service not wired")
router=APIRouter(prefix="/api/inventory/minimax",tags=["minimax"])
@router.get("/{warehouse}")
def preview(warehouse: int=Path(gt=0),user: MinimaxUser=Depends(minimax_view),
            service: MinimaxPort=Depends(minimax_service))->dict[str,Any]:
    return service.preview(warehouse)
@router.post("/{warehouse}/reconcile")
def reconcile(warehouse: int=Path(gt=0),user: MinimaxUser=Depends(minimax_edit),
              service: MinimaxPort=Depends(minimax_service))->dict[str,Any]:
    return service.reconcile(warehouse,user.username)
