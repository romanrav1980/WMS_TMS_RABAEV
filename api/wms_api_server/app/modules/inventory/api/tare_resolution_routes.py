from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator,field_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_tare import TareError,TarePort,tare_service
router=APIRouter(prefix="/api/inventory/tare",tags=["tare-damage-resolutions"])

class Resolution(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}$")
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

class Damage(Resolution):
    owner_ware_id: int=Field(strict=True,ge=1)
    pallet_type_id: int=Field(strict=True,ge=1)
    custodian_kind: Literal["WAREHOUSE","VEHICLE","STORE"]
    custodian_id: str=Field(strict=True,min_length=1,max_length=255)
    delivery_accept_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)
    task_id: int|None=Field(default=None,strict=True,ge=1)
    scan_vehicle: str|None=Field(default=None,strict=True,min_length=1,max_length=50)

    @field_validator("custodian_id")
    @classmethod
    def bytes_limit(cls,value: str) -> str:
        if len(value.encode("utf-8"))>255:raise ValueError("Custodian exceeds255 UTF-8 bytes")
        return value

    @model_validator(mode="after")
    def source_required(self) -> "Damage":
        if self.custodian_kind=="STORE" and not self.delivery_accept_operation_id:
            raise ValueError("Store damage requires original delivery")
        if self.custodian_kind=="VEHICLE" and(not self.task_id or not self.scan_vehicle):
            raise ValueError("Vehicle damage requires current trip and vehicle scan")
        return self

class Writeoff(Resolution):
    writeoff_warehouse_id: int|None=Field(default=None,strict=True,ge=1)
    damage_operation_id: str=Field(strict=True,min_length=1,max_length=100)

def post(service: TarePort,body: Resolution,kind: str,source_keys: tuple[str,...],user: AdminUser) -> dict[str,Any]:
    values=body.model_dump()
    if values.get("writeoff_warehouse_id")is None:values.pop("writeoff_warehouse_id",None)
    operation=values.pop("operation_id");source={key:values.pop(key) for key in source_keys}
    try:return service.post(kind,operation,source,values,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":exc.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.post("/damage")
def damage(body: Damage,user: AdminUser=Depends(require_permission("tare_damage")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_DAMAGE",("task_id","delivery_accept_operation_id"),user)

@router.post("/writeoff")
def writeoff(body: Writeoff,user: AdminUser=Depends(require_permission("tare_writeoff")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_WRITE_OFF",("damage_operation_id",),user)

@router.get("/warehouses/{ware_id}/damage-cases")
def cases(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> list[dict[str,Any]]:
    return service.damage_cases(ware_id,user.username)
