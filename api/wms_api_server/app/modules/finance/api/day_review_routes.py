from datetime import date
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import LogisticsCostError
from ..contracts_day_reviews import DayReviewsPort,day_reviews_service

router=APIRouter(prefix="/api/finance/day-reconciliation",tags=["warehouse-day-reconciliation"])

class ReviewBody(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int=Field(strict=True,gt=0)
    business_date: date
    timezone_region: str=Field(min_length=1,max_length=64)
    expected_version: int=Field(strict=True,ge=0)
    source_hash: str=Field(pattern=r"^[a-f0-9]{64}$")
    reason: str=Field(min_length=8,max_length=500)

@router.get("/warehouses/{ware_id}/review-context")
def context(ware_id: int,business_date: date,timezone_region: str=Query(min_length=1,max_length=64),
            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.context(ware_id,business_date,timezone_region,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.post("/reviews",status_code=201)
def record(body: ReviewBody,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
           service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.record(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.post("/reviews/resolve")
def resolve(body: ReviewBody,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.resolve(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.get("/reviews/warehouses/{ware_id}/history")
def history(ware_id: int,business_date: date,timezone_region: str=Query(min_length=1,max_length=64),
            after_version: int=Query(default=0,ge=0),limit: int=Query(default=20,ge=1,le=50),
            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.history(ware_id,business_date,timezone_region,after_version,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/reviews/{operation}")
def detail(operation: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
           service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.get(operation,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.get("/warehouses/{ware_id}/shipping-register")
def shipping_register(ware_id: int,business_date: date,after_id: int=Query(default=0,ge=0),limit: int=Query(default=20,ge=1,le=50),
                      user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                      service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.shipping_register(ware_id,business_date,after_id,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc


class InspectionBody(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    review_operation_id: str=Field(min_length=1,max_length=100)
    source_hash: str=Field(pattern=r"^[a-f0-9]{64}$")
    inspection_role: Literal["WAREHOUSE_CHIEF","DISPATCHER"]
    observed_empty: bool=Field(strict=True)
    note: str=Field(min_length=8,max_length=500)


@router.get("/reviews/{review_id}/shipping-inspections")
def inspection(review_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
               service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.inspection(review_id,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc


@router.post("/shipping-inspections",status_code=201)
def inspect(body: InspectionBody,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.inspect(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id})from exc


@router.post("/shipping-inspections/resolve")
def resolve_inspection(body: InspectionBody,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                       service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.resolve_inspection(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id})from exc
