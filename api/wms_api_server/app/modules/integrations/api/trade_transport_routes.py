from collections.abc import Callable
from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path,Query
from ...platform.public import AdminUser,get_current_user
from ..contracts_trade_transport import TripBinding,TransportDocumentResult,TradeTransportPort,TradeTransportError
from ..contracts_trade_topup import TopupConfirm,TopupDecision,TopupPreview,TopupRelease,TopupSapReply,TopupSave
router=APIRouter(prefix="/api/tradecase/warehouses/{warehouse}/trips/{trip}",tags=["tradecase-transport-documents"])

def trade_transport_service()->TradeTransportPort:raise RuntimeError("Trade transport not wired")

@router.post("/topup-preview")
def topup(body:TopupPreview,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.topup(warehouse,trip,body,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{'code':exc.code})from exc

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

@router.get("/coverage")
def coverage(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    """Ordered/reserved/picked/loaded/departed by the trip's real order lines; one READ ONLY snapshot, unknown is null."""
    try:return service.coverage(warehouse,trip,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("/route-points")
def route_points(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    """Route stops of the bound warehouse trip linked to TRADECASE recipients by keys only; READ ONLY."""
    try:return service.route_points(warehouse,trip,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

@router.get("/capacity")
def capacity(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),sku_id:str=Query(min_length=1,max_length=100),requested_boxes:int=Query(ge=1,le=100000),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.capacity(warehouse,trip,sku_id,requested_boxes,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

# Durable top-up decisions. Save/adjust/reject never touch stock; confirm/release/SAP rejection go through StockPosting.
Proposal=Path(gt=0)

def _topup(call:Callable[[],dict[str,Any]])->dict[str,Any]:
    try:return call()
    except TradeTransportError as exc:
        uncertain=exc.status in {401,403,404,503} or exc.code in {"OPERATION_CONFLICT","TRADE_TOPUP_OPERATION_CONFLICT","TRADE_TOPUP_EVENT_CONFLICT"}
        raise HTTPException(exc.status,{"code":exc.code,"outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain})from exc

@router.get("/topup-proposals")
def topup_list(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().list(warehouse,trip,user.username))

@router.post("/topup-proposals")
def topup_save(body:TopupSave,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().save(warehouse,trip,body,user.username))

@router.post("/topup-proposals/{proposal}/decision")
def topup_decide(body:TopupDecision,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),proposal:int=Proposal,user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().decide(warehouse,trip,proposal,body,user.username))

@router.post("/topup-proposals/{proposal}/confirm")
def topup_confirm(body:TopupConfirm,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),proposal:int=Proposal,user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().confirm(warehouse,trip,proposal,body,user.username))

@router.post("/topup-proposals/{proposal}/release")
def topup_release(body:TopupRelease,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),proposal:int=Proposal,user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().release(warehouse,trip,proposal,body,user.username))

@router.post("/topup-proposals/{proposal}/sap-reply")
def topup_sap_reply(body:TopupSapReply,warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),proposal:int=Proposal,user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    return _topup(lambda:service.proposals().sap_reply(warehouse,trip,proposal,body,user.username))
