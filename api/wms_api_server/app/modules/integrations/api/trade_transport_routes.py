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

@router.get("/capacity")
def capacity(warehouse:int=Path(gt=0),trip:str=Path(min_length=1,max_length=100),sku_id:str=Query(min_length=1,max_length=100),requested_boxes:int=Query(ge=1,le=100000),user:AdminUser=Depends(get_current_user),service:TradeTransportPort=Depends(trade_transport_service))->dict[str,Any]:
    try:return service.capacity(warehouse,trip,sku_id,requested_boxes,user.username)
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code})from exc

# Durable top-up decisions. Save/adjust/reject never touch stock; confirm/release/SAP rejection go through StockPosting.
Proposal=Path(gt=0)

def _topup(call)->dict[str,Any]:
    try:return call()
    except TradeTransportError as exc:raise HTTPException(exc.status,{"code":exc.code,"outcome_confirmed":exc.status!=503,"retry_same_operation_id":exc.status==503})from exc

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
