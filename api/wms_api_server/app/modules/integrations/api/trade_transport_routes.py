from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path
from ...platform.public import AdminUser,get_current_user
from ..contracts_trade_transport import TripBinding,TransportDocumentResult,TradeTransportPort,TradeTransportError
router=APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/trips/{trip}",tags=["tradecase-transport-documents"])

def trade_transport_service()->TradeTransportPort:raise RuntimeError("Trade transport not wired")

@router.post("/binding")
def bind(body:TripBinding,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.bind(warehouse,trip,body,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.post("/transport-document")
def result(body:TransportDocumentResult,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.result(warehouse,trip,body,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("/execution")
def state(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.state(warehouse,trip,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc
