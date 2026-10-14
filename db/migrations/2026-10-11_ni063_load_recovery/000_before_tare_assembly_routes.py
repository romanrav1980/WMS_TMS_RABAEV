from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_tare import TarePort,TareError,tare_service
from ..contracts_tare_assembly import TareAssemblyPort,tare_assembly_service
router=APIRouter(prefix="/api/inventory/tare",tags=["existing-assembly-tare"])

class Book(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    place_kind: Literal["CASE","HU"]
    place_id: str=Field(strict=True,min_length=1,max_length=200)
    expected_warehouse_id: int|None=Field(default=None,strict=True,ge=1)
    pallet_type_id: int|None=Field(default=None,strict=True,ge=1)

    @model_validator(mode="after")
    def place_required(self) -> "Book":
        if len(self.place_id.encode("utf-8"))>200:raise ValueError("Place identifier exceeds200 UTF-8 bytes")
        if self.place_kind=="HU" and self.pallet_type_id is None:raise ValueError("Container requires actual pallet type")
        if self.place_kind=="CASE" and(not self.place_id.isascii() or not self.place_id.isdecimal() or int(self.place_id)<1):
            raise ValueError("CASE requires existing task number")
        return self

class Cancel(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    booking_operation_id: str=Field(strict=True,min_length=1,max_length=100)

def command(service: TarePort,kind: str,operation_id: str,source: dict[str,Any],metadata: dict[str,Any],user: AdminUser) -> dict[str,Any]:
    try:return service.post(kind,operation_id,source,metadata,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":exc.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.post("/book")
def book(body: Book,user: AdminUser=Depends(require_permission("tare_plan")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    metadata={"pallet_type_id":body.pallet_type_id}
    if body.expected_warehouse_id is not None:metadata["expected_warehouse_id"]=body.expected_warehouse_id
    return command(service,"TARE_BOOK",body.operation_id,{"place_kind":body.place_kind,"place_id":body.place_id},metadata,user)

@router.post("/book-cancel")
def cancel(body: Cancel,user: AdminUser=Depends(require_permission("tare_plan")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return command(service,"TARE_BOOK_CANCEL",body.operation_id,{"booking_operation_id":body.booking_operation_id},{},user)

@router.get("/warehouses/{ware_id}/availability")
def availability(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str,Any]]:
    try:return service.availability(ware_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/warehouses/{ware_id}/bookings")
def bookings(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str,Any]]:
    try:return service.bookings(ware_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/assembly/catalog")
def catalog(user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str,Any]:
    return service.catalog(user.username)

@router.get("/warehouses/{ware_id}/trips/{task_id}/loaded-bookings")
def loaded_bookings(ware_id: int,task_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str,Any]]:
    try:return service.loaded_bookings(ware_id,task_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/warehouses/{ware_id}/waves/{wave_id}/forecast")
def forecast(ware_id: int,wave_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str,Any]:
    try:return service.forecast(ware_id,wave_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
