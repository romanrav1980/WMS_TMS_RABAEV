from typing import Annotated,Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,field_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_tare import TareError,TarePort,tare_service
router=APIRouter(prefix="/api/inventory/tare",tags=["returnable-tare"])

class Operation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")

class Count(Operation):
    owner_ware_id: int=Field(strict=True,ge=1)
    pallet_type_id: int=Field(strict=True,ge=1)
    condition: Literal["GOOD","DAMAGED"]
    observed_quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

class Offer(Operation):
    task_id: int=Field(strict=True,ge=1)
    owner_ware_id: int=Field(strict=True,ge=1)
    pallet_type_id: int=Field(strict=True,ge=1)
    condition: Literal["GOOD","DAMAGED"]
    damage_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    from_kind: Literal["WAREHOUSE","VEHICLE","STORE"]
    from_id: str=Field(strict=True,min_length=1,max_length=255)
    to_kind: Literal["WAREHOUSE","VEHICLE","STORE"]
    to_id: str=Field(strict=True,min_length=1,max_length=255)
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}$")
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)
    booking_operation_ids: list[Annotated[str,Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")]]=Field(default_factory=list,max_length=100)

    @field_validator("from_id","to_id","scan_vehicle")
    @classmethod
    def byte_length(cls,value: str) -> str:
        if len(value.encode("utf-8"))>255:raise ValueError("Identifier exceeds255 UTF-8 bytes")
        return value

class OfferCancel(Operation):
    offer_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)
    reason: str=Field(strict=True,min_length=1,max_length=500)

class Accept(Operation):
    offer_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    accepted_quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}$")
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)

def post(service: TarePort,body: Operation,kind: str,source_fields: tuple[str,...],user: AdminUser) -> dict[str,Any]:
    values=body.model_dump();
    if values.get("booking_operation_ids")==[]:values.pop("booking_operation_ids",None)
    damage=values.pop("damage_operation_id",None)
    operation=values.pop("operation_id");source={name:values.pop(name) for name in source_fields}
    if damage is not None:source["damage_operation_id"]=damage
    try:return service.post(kind,operation,source,values,user.username)
    except TareError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":exc.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.post("/count")
def count(body: Count,user: AdminUser=Depends(require_permission("tare_adjust")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_COUNT",(),user)

@router.post("/offer")
def offer(body: Offer,user: AdminUser=Depends(require_permission("tare_offer")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_OFFER",("task_id",),user)

@router.post("/accept")
def accept(body: Accept,user: AdminUser=Depends(require_permission("tare_accept")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_ACCEPT",("offer_operation_id",),user)

@router.post("/offer-cancel")
def offer_cancel(body: OfferCancel,user: AdminUser=Depends(require_permission("tare_offer")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_OFFER_CANCEL",("offer_operation_id",),user)

@router.get("/warehouses/{ware_id}/balances")
def balances(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> list[dict[str,Any]]:
    return service.balances(ware_id,user.username)

@router.get("/trips/{task_id}/offers")
def offers(task_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> list[dict[str,Any]]:
    return service.offers(task_id,user.username)

@router.get("/trips/{task_id}/context")
def context(task_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    try:return service.context(task_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.get("/warehouses/{ware_id}/damage-custody")
def damage_custody(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    if ware_id<1:raise HTTPException(422,"Укажите склад-владелец")
    try:return service.damage_custody(ware_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
