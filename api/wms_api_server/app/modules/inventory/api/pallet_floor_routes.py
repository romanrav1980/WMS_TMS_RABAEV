from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,get_current_user
from ..contracts_pallet_floor import PalletFloorPort,pallet_floor_service
from ..contracts_stock import StockPostingError

router=APIRouter(prefix="/api/inventory/pallet-floor-types",tags=["existing-stock-pallet-type"])

class PalletFloorRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    identifier: str=Field(strict=True,min_length=1,max_length=200,pattern=r"^[^\x00]+$")
    pallet_type_id: int=Field(strict=True,ge=1)
    expected_version: int=Field(strict=True,ge=0)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=200,pattern=r"^[^\x00]+$")
    scan_cell: str=Field(strict=True,min_length=1,max_length=60,pattern=r"^[^\x00]+$")
    evidence_reference: str=Field(strict=True,min_length=1,max_length=100)

def failure(exc: StockPostingError)->HTTPException:
    uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","LOCK_RETRY_EXHAUSTED","CONNECTION_UNUSABLE","STOCK_RELEASE_NOT_ACTIVE"}
    denied=exc.oracle_code==20882
    conflict="OPERATION_CONFLICT" in (exc.rule_reason or exc.code)
    status=503 if uncertain else 403 if denied else 409
    return HTTPException(status,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":exc.operation_id,
        "outcome_confirmed":not (uncertain or denied or conflict),"retry_same_operation_id":uncertain or denied or conflict})

@router.get("")
def read(identifier: str=Query(min_length=1,max_length=200),
         user: AdminUser=Depends(get_current_user),
         service: PalletFloorPort=Depends(pallet_floor_service))->dict[str,Any]:
    try:return service.read(identifier,user.username)
    except StockPostingError as exc:raise failure(exc)from exc

@router.post("")
def confirm(body: PalletFloorRequest,user: AdminUser=Depends(get_current_user),
            service: PalletFloorPort=Depends(pallet_floor_service))->dict[str,Any]:
    try:
        values=body.model_dump(mode="json")
        return service.confirm(body.operation_id,body.identifier,{k:v for k,v in values.items()if k not in {"operation_id","identifier"}},user.username)
    except StockPostingError as exc:raise failure(exc)from exc
    except ValueError as exc:raise HTTPException(422,str(exc))from exc
