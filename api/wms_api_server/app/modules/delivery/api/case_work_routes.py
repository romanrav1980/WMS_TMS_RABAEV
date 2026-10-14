from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import StoreReceiptError
from ..contracts_case_work import CaseWorkPort,case_work_service
from .store_receipt_routes import failure

router=APIRouter(prefix="/api/delivery/case-work",tags=["store-investigation"])


class CaseCommand(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_version: int=Field(strict=True,ge=1)


class Assignment(CaseCommand):
    expedition_user: str=Field(strict=True,min_length=1,max_length=50)
    security_user: str=Field(strict=True,min_length=1,max_length=50)
    search_deadline: str=Field(strict=True,pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+00:00$")


class Finding(CaseCommand):
    role: Literal["EXPEDITION","SECURITY"]
    report: str=Field(strict=True,min_length=1,max_length=2000)


class Loss(CaseCommand):
    line_no: int=Field(strict=True,ge=1,le=200)
    reason: str=Field(strict=True,min_length=1,max_length=2000)


def send(service: CaseWorkPort,case_id: str,body: CaseCommand,action: str,actor: str) -> dict[str,Any]:
    if not 1<=len(case_id)<=100:
        raise HTTPException(422,"Укажите разбирательство")
    metadata={"action":action,**body.model_dump(exclude={"operation_id"})}
    try:
        return service.command(body.operation_id,case_id,metadata,actor)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.post("/{case_id}/assign")
def assign(case_id: str,body: Assignment,user: AdminUser=Depends(require_permission("store_case_manage")),
           service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    return send(service,case_id,body,"ASSIGN",user.username)


@router.post("/{case_id}/finding")
def finding(case_id: str,body: Finding,user: AdminUser=Depends(require_permission("store_case_investigate")),
            service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    return send(service,case_id,body,"FINDING",user.username)


@router.post("/{case_id}/loss")
def loss(case_id: str,body: Loss,user: AdminUser=Depends(require_permission("store_loss_confirm")),
         service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    return send(service,case_id,body,"LOSS_CONFIRM",user.username)


@router.get("/mine")
def mine(user: AdminUser=Depends(require_permission("store_case_investigate")),
         service: CaseWorkPort=Depends(case_work_service)) -> list[dict[str,Any]]:
    return service.assigned(user.username)


@router.get("/{case_id}/investigation")
def investigation(case_id: str,user: AdminUser=Depends(require_permission("store_case_investigate")),
                  service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    try:
        return service.investigation(case_id,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/{case_id}/loss-review")
def review(case_id: str,user: AdminUser=Depends(require_permission("store_loss_confirm")),
           service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    try:
        return service.review(case_id,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/{case_id}/management")
def management(case_id: str,user: AdminUser=Depends(require_permission("store_case_manage")),
               service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    try:
        return service.review(case_id,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc

class Closure(CaseCommand):
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.post("/{case_id}/close")
def close(case_id: str,body: Closure,user: AdminUser=Depends(require_permission("store_loss_confirm")),service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    return send(service,case_id,body,"CLOSE",user.username)
