"""Read bounded replenishment facts through a typed port."""
from typing import Any,Protocol
from fastapi import APIRouter,Depends,Query

class ReplenishmentProgressPort(Protocol):
    def list_rows(self,wave_id: int,limit: int) -> list[dict[str,Any]]: ...

def replenishment_view() -> object:
    raise RuntimeError("Replenishment view permission not wired")

def replenishment_progress_service() -> ReplenishmentProgressPort:
    raise RuntimeError("Replenishment progress service not wired")

router=APIRouter(prefix="/api/inventory",tags=["replenishment-progress"])

@router.get("/replenishment-progress")
def replenishment_progress(wave_id: int=Query(gt=0),limit: int=Query(default=50,ge=1,le=100),
    user: object=Depends(replenishment_view),
    service: ReplenishmentProgressPort=Depends(replenishment_progress_service)) -> list[dict[str,Any]]:
    return service.list_rows(wave_id,limit)
