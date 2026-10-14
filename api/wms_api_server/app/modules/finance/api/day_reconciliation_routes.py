from datetime import date
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Query,Path
from ...platform.public import AdminUser,require_permission
from ..contracts import LogisticsCostError
from ..contracts_reconciliation import DayReconciliationPort,day_reconciliation_service
router=APIRouter(prefix="/api/finance/day-reconciliation",tags=["warehouse-day-reconciliation"])

@router.get("/warehouses/{ware_id}")
def report(ware_id: int,business_date: date,timezone_region: str=Query(default="Asia/Tbilisi",min_length=1,max_length=64),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: DayReconciliationPort=Depends(day_reconciliation_service)) -> dict[str,Any]:
    try:return service.report(ware_id,business_date,timezone_region,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.get("/warehouses/{ware_id}/stock-conflicts")
def stock_conflicts(ware_id: int=Path(gt=0),metric: Literal["stock_quantity_invariants","physical_unit_composition"]=Query(...),
                    after: str | None=Query(None,max_length=2048),limit: int=Query(50,ge=1,le=100),
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: DayReconciliationPort=Depends(day_reconciliation_service)) -> dict[str,Any]:
    try:return service.stock_conflicts(ware_id,metric,after,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
