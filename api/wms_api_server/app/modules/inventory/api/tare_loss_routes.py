from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_tare import TarePort,TareError,tare_service
from ..contracts_tare_assembly import TareAssemblyPort,tare_assembly_service
router=APIRouter(prefix="/api/inventory/tare",tags=["warehouse-tare-loss"])

class Operation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

class Report(Operation):
    owner_ware_id: int=Field(strict=True,ge=1)
    pallet_type_id: int=Field(strict=True,ge=1)
    condition: Literal["GOOD","DAMAGED"]
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}$")
    expected_version: int=Field(strict=True,ge=1)
    custodian_kind: Literal["WAREHOUSE","STORE","VEHICLE"]|None=None
    custodian_id: str|None=Field(default=None,strict=True,min_length=1,max_length=255)
    source_claim_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)
    task_id: int|None=Field(default=None,strict=True,ge=1)
    scan_vehicle: str|None=Field(default=None,strict=True,min_length=1,max_length=50)

    @model_validator(mode="after")
    def source_required(self) -> "Report":
        if self.custodian_kind=="STORE" and(not self.custodian_id or not self.source_claim_id):raise ValueError("Store loss requires original claim and current store")
        if self.custodian_kind=="VEHICLE" and(not self.custodian_id or not self.task_id or not self.scan_vehicle):raise ValueError("Vehicle loss requires current trip/id/scan")
        if self.custodian_id and len(self.custodian_id.encode("utf-8"))>255:raise ValueError("Holder identifier exceeds255 bytes")
        return self

class Decision(Operation):
    claim_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    outcome: Literal["WRITE_OFF","REJECT"]

def post(service: TarePort,body: Operation,kind: str,user: AdminUser) -> dict[str,Any]:
    metadata=body.model_dump();operation=metadata.pop("operation_id");source={}
    if isinstance(body,Report):
        for key in ("source_claim_id","task_id"):
            value=metadata.pop(key,None)
            if value is not None:source[key]=value
        for key in ("custodian_kind","custodian_id","scan_vehicle"):
            if metadata.get(key) is None:metadata.pop(key,None)
    if isinstance(body,Decision):source["claim_operation_id"]=metadata.pop("claim_operation_id")
    try:return service.post(kind,operation,source,metadata,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":exc.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.post("/loss-report")
def report(body: Report,user: AdminUser=Depends(require_permission("tare_loss_report")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_LOSS_REPORT",user)

@router.post("/loss-decide")
def decide(body: Decision,user: AdminUser=Depends(require_permission("tare_writeoff")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    return post(service,body,"TARE_LOSS_DECIDE",user)

@router.get("/warehouses/{ware_id}/loss-cases")
def cases(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str,Any]]:
    try:return service.loss_cases(ware_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
