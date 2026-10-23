"""Typed pool commands; request callers cannot supply allocation planning hints."""
from typing import Any,Protocol
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field

class PoolUser(Protocol):
    username: str

class PoolPort(Protocol):
    def preview(self,warehouse: int,article: str,actor: str) -> dict[str,Any]: ...
    def allocate(self,warehouse: int,article: str,operation_id: str,actor: str) -> dict[str,Any]: ...

def pool_view() -> PoolUser:
    raise RuntimeError("Pool view rights not wired")

def pool_edit() -> PoolUser:
    raise RuntimeError("Pool edit rights not wired")

def pool_service() -> PoolPort:
    raise RuntimeError("Pool service not wired")

class PoolCommandInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100)

router=APIRouter(prefix="/api/inventory/soft-pools",tags=["soft-demand-pool"])

@router.get("/{warehouse}/{article}")
def preview(warehouse: int=Path(gt=0),article: str=Path(min_length=1,max_length=160),
            user: PoolUser=Depends(pool_view),service: PoolPort=Depends(pool_service)) -> dict[str,Any]:
    try:
        return service.preview(warehouse,article,user.username)
    except PermissionError as exc:  # C-0162: current warehouse scope of the reader
        raise HTTPException(403,{"code":str(exc) or "POOL_WAREHOUSE_ACCESS_DENIED"}) from exc

@router.post("/{warehouse}/{article}/allocate")
def allocate(request: PoolCommandInput,warehouse: int=Path(gt=0),article: str=Path(min_length=1,max_length=160),
             user: PoolUser=Depends(pool_edit),service: PoolPort=Depends(pool_service)) -> dict[str,Any]:
    return service.allocate(warehouse,article,request.operation_id,user.username)
