from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import StoreReceiptError
from ..contracts_returns import StoreReturnsPort,store_returns_service
from .store_receipt_routes import failure

router=APIRouter(prefix="/api/delivery/store-returns",tags=["store-returns"])


class ReturnApproval(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    line_no: int=Field(strict=True,ge=1,le=200)
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    return_basis: Literal["ACCEPTED","REFUSED","DAMAGED"]="ACCEPTED"
    disposition: Literal["REUSE","SUPPLIER","DISPOSAL"]
    reason: str=Field(strict=True,min_length=1,max_length=2000)
    decision_reference: str=Field(strict=True,min_length=1,max_length=255)
    unit_keys: list[str]=Field(default_factory=list,max_length=10000)
    complete_good_box: bool=Field(strict=True,default=False)


@router.post("/{receipt_id}/approve")
def approve(receipt_id: str,body: ReturnApproval,user: AdminUser=Depends(require_permission("store_return_approve")),
            service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str,Any]:
    if not 1<=len(receipt_id)<=100:
        raise HTTPException(422,"Укажите исходную приёмку")
    try:
        return service.approve(body.operation_id,receipt_id,body.line_no,{**body.model_dump(exclude={"operation_id","line_no","unit_keys","return_basis"}),**({"unit_keys":body.unit_keys} if body.unit_keys else {}),**({"return_basis":body.return_basis}if body.return_basis!="ACCEPTED"else {})},user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/{receipt_id}")
def original(receipt_id: str,user: AdminUser=Depends(require_permission("store_return_approve")),
             service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str,Any]:
    try:
        return service.original(receipt_id,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/{receipt_id}/reuse-preview")
def reuse_preview(receipt_id: str,line_no: int=Query(ge=1,le=200),
                  quantity: str=Query(pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$"),
                  user: AdminUser=Depends(require_permission("store_return_approve")),
                  service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str,Any]:
    if not 1<=len(receipt_id)<=100:raise HTTPException(422,"Укажите исходную приёмку")
    try:return service.reuse_preview(receipt_id,line_no,quantity,user.username)
    except StoreReceiptError as exc:raise failure(exc)from exc
