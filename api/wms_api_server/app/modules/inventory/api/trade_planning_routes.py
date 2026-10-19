from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path
from ...platform.public import AdminUser,get_current_user
from ..contracts_trade_planning import TradeOrderBind,TradePlanningPort,TradePlanningError
router=APIRouter(prefix="/api/tradecase/warehouses/{warehouse}",tags=["tradecase-planning"])

def trade_planning_service()->TradePlanningPort:
    raise RuntimeError("TRADECASE planning not wired")

@router.post("/orders/{order}/binding")
def bind(body:TradeOrderBind,warehouse:int=Path(gt=0),order:str=Path(min_length=1,max_length=100),
         user:AdminUser=Depends(get_current_user),service:TradePlanningPort=Depends(trade_planning_service))->dict[str,Any]:
    try:return service.bind(warehouse,order,body,user.username)
    except TradePlanningError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc
