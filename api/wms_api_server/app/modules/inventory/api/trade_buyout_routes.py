from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path,Query
from ...platform.public import AdminUser,get_current_user
from ..contracts_trade_buyout import TradeBuyoutPort,TradeBuyoutRequest,TradeBuyoutResult
from ..contracts_trade_stock import TradeStockError
router=APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/buyouts",tags=["tradecase-buyouts"])
def trade_buyout_service()->TradeBuyoutPort:raise RuntimeError("TRADECASE buyout not wired")

@router.post("")
def request(body:TradeBuyoutRequest,warehouse:int=Path(gt=0),user:AdminUser=Depends(get_current_user),service:TradeBuyoutPort=Depends(trade_buyout_service))->dict[str,Any]:
    try:return service.request_buyout(warehouse,body,user.username)
    except TradeStockError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.post("/results")
def result(body:TradeBuyoutResult,warehouse:int=Path(gt=0),user:AdminUser=Depends(get_current_user),service:TradeBuyoutPort=Depends(trade_buyout_service))->dict[str,Any]:
    try:return service.buyout_result(warehouse,body,user.username)
    except TradeStockError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("")
def listing(warehouse:int=Path(gt=0),after:int=Query(default=0,ge=0),limit:int=Query(default=50,ge=1,le=100),pending_only:bool=False,user:AdminUser=Depends(get_current_user),service:TradeBuyoutPort=Depends(trade_buyout_service))->dict[str,Any]:
    try:return service.read_buyouts(warehouse,"BUYOUT_LIST","",str(after),limit,pending_only,user.username)
    except TradeStockError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("/{identity}")
def detail(identity:str=Path(min_length=1,max_length=100),warehouse:int=Path(gt=0),user:AdminUser=Depends(get_current_user),service:TradeBuyoutPort=Depends(trade_buyout_service))->dict[str,Any]:
    try:return service.read_buyouts(warehouse,"BUYOUT_DETAIL",identity,"",1,False,user.username)
    except TradeStockError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("/{identity}/units")
def units(identity:str=Path(min_length=1,max_length=100),warehouse:int=Path(gt=0),after:str=Query(default="",max_length=64),limit:int=Query(default=50,ge=1,le=100),user:AdminUser=Depends(get_current_user),service:TradeBuyoutPort=Depends(trade_buyout_service))->dict[str,Any]:
    try:return service.read_buyouts(warehouse,"BUYOUT_UNITS",identity,after,limit,False,user.username)
    except TradeStockError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc
