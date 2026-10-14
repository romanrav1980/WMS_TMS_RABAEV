from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field,model_validator,field_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_tare import TareError
from ..contracts_tare_policy import TarePolicyPort,tare_policy_service
router=APIRouter(prefix="/api/inventory/tare",tags=["tare-return-deadlines"])

class ReturnPolicy(BaseModel):
    model_config=ConfigDict(extra="forbid")
    scope_kind: Literal["STORE","CUSTOMER"]
    scope_key: str=Field(strict=True,min_length=1,max_length=255)
    return_mode: Literal["NEXT_DELIVERY","DAYS","SAME_DAY"]
    return_days: int|None=Field(default=None,strict=True,ge=1,le=3660)
    timezone_region: str=Field(strict=True,min_length=1,max_length=64)
    expected_version: int=Field(strict=True,ge=0)

    @field_validator("scope_key")
    @classmethod
    def bytes_limit(cls,value: str) -> str:
        if len(value.encode("utf-8"))>255:raise ValueError("Scope exceeds255 UTF-8 bytes")
        return value

    @model_validator(mode="after")
    def days_required(self) -> "ReturnPolicy":
        if (self.return_mode=="DAYS")!=(self.return_days is not None):
            raise ValueError("DAYS requires a day count; other modes require null")
        return self

@router.get("/return-policy")
def read(scope_kind: Literal["STORE","CUSTOMER"],scope_key: str=Query(min_length=1,max_length=255),
         user: AdminUser=Depends(require_permission("warehouse_settings_edit")),service: TarePolicyPort=Depends(tare_policy_service)) -> dict[str,Any]:
    return service.read(scope_kind,scope_key)

@router.put("/return-policy")
def configure(body: ReturnPolicy,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
              service: TarePolicyPort=Depends(tare_policy_service)) -> dict[str,Any]:
    values=body.model_dump();kind=values.pop("scope_kind");key=values.pop("scope_key")
    try:return service.configure(kind,key,values,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/warehouses/{ware_id}/store-debt")
def debt(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),
         service: TarePolicyPort=Depends(tare_policy_service)) -> list[dict[str,Any]]:
    return service.debt(ware_id,user.username)
