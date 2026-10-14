"""Warehouse/SKU fulfillment policy, with explicit inherited stock-backed default."""
from typing import Any,Literal,Protocol
from fastapi import APIRouter,Depends,Path
from pydantic import BaseModel,ConfigDict,Field

class AllocationUser(Protocol):
    username: str

class AllocationPolicyInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    expected_version: int=Field(strict=True,ge=0)
    stock_class: Literal["DRY_RACK","FRESH","OTHER"]
    ship_from_stock: bool | None=None
    pick_step: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")

class AllocationPolicyPort(Protocol):
    def get(self,warehouse: int,article: str) -> dict[str,Any]: ...
    def set(self,warehouse: int,article: str,request: AllocationPolicyInput,actor: str) -> dict[str,Any]: ...

def allocation_policy_view() -> AllocationUser:
    raise RuntimeError("Allocation policy read rights not wired")

def allocation_policy_edit() -> AllocationUser:
    raise RuntimeError("Allocation policy edit rights not wired")

def allocation_policy_service() -> AllocationPolicyPort:
    raise RuntimeError("Allocation policy service not wired")

router=APIRouter(prefix="/api/sku-allocation",tags=["sku-allocation"])

@router.get("/{warehouse}/{article}")
def get_policy(warehouse: int=Path(gt=0),article: str=Path(min_length=1,max_length=160),
               user: AllocationUser=Depends(allocation_policy_view),service: AllocationPolicyPort=Depends(allocation_policy_service)) -> dict[str,Any]:
    return service.get(warehouse,article)

@router.put("/{warehouse}/{article}")
def set_policy(request: AllocationPolicyInput,warehouse: int=Path(gt=0),article: str=Path(min_length=1,max_length=160),
               user: AllocationUser=Depends(allocation_policy_edit),service: AllocationPolicyPort=Depends(allocation_policy_service)) -> dict[str,Any]:
    return service.set(warehouse,article,request,user.username)
