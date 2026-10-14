from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_case_type import CaseTypePort,case_type_service
from ..contracts_stock import StockPostingError

router=APIRouter(prefix="/api/case-pick/tasks",tags=["existing-case-pallet-type"])

class CaseTypeRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    pallet_type_id: int=Field(strict=True,ge=1)
    expected_version: int=Field(strict=True,ge=0)
    scan_container: str=Field(strict=True,min_length=1,max_length=200)
    reason: str=Field(strict=True,min_length=1,max_length=500)

def failure(exc: StockPostingError)->HTTPException:
    uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
    return HTTPException(503 if uncertain else 403 if exc.oracle_code==20882 else 409,
        {"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":exc.operation_id,
         "outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain})

@router.get("/{task_id}/pallet-type")
def read(task_id: int=Path(ge=1),user: AdminUser=Depends(require_permission("case_pick_view")),
         service: CaseTypePort=Depends(case_type_service))->dict[str,Any]:
    try:return service.read(task_id,user.username)
    except StockPostingError as exc:raise failure(exc)from exc

@router.post("/{task_id}/pallet-type")
def change(body: CaseTypeRequest,task_id: int=Path(ge=1),user: AdminUser=Depends(require_permission("case_pick_execute")),
           service: CaseTypePort=Depends(case_type_service))->dict[str,Any]:
    try:
        values=body.model_dump(mode="json")
        return service.change(task_id,body.operation_id,{k:v for k,v in values.items()if k!="operation_id"},user.username)
    except StockPostingError as exc:raise failure(exc)from exc
    except ValueError as exc:raise HTTPException(422,str(exc))from exc
