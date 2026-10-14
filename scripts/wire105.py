from pathlib import Path
import json
out={}
out["api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py"]='''from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
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

class Decision(Operation):
    claim_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    outcome: Literal["WRITE_OFF","REJECT"]

def post(service: TarePort,body: Operation,kind: str,user: AdminUser) -> dict[str,Any]:
    metadata=body.model_dump();operation=metadata.pop("operation_id");source={}
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
'''
p=Path("api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def catalog(","    def loss_cases(self,ware_id: int,actor: str) -> list[dict[str,Any]]: ...\n    def catalog(",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("    def catalog(",'''    def loss_cases(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select c.OPERATION_ID,c.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,c.CONDITION_CODE,
                   to_char(c.QUANTITY,'TM9') QUANTITY,c.REASON_TEXT,c.DECISION_REFERENCE,c.ACTOR,c.CREATED_AT,
                   d.OPERATION_ID DECISION_OPERATION_ID,d.OUTCOME,d.ACTOR DECIDED_BY
              from RRL_TARE_LOSS_CLAIM c join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID
               left join RRL_TARE_LOSS_DECISION d on d.CLAIM_OPERATION_ID=c.OPERATION_ID
             where c.OWNER_WARE_ID=:ware order by c.CREATED_AT desc,c.OPERATION_ID fetch first 200 rows only
        """,{"ware":ware_id})

    def catalog(''',1).replace("to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,a.BALANCE_VERSION,","to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,to_char(a.LOSS_PENDING_QTY,'TM9') LOSS_PENDING_QUANTITY,a.BALANCE_VERSION,",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nfrom .api.tare_loss_routes import router as tare_loss_router\n"
p=Path("api/wms_api_server/app/main.py");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nfrom .modules.inventory.public import tare_loss_router\napp.include_router(tare_loss_router)\n"
print(json.dumps(out,ensure_ascii=True))
