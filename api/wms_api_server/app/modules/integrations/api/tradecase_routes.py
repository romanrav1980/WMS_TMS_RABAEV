"""Authenticated document intake; native warehouse grants are checked on every call."""
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ...platform.public import AdminUser, get_current_user
from ..contracts_tradecase import TradecaseDocuments, TradecaseError, TradeEnvelope, TradeSiteSetting

router = APIRouter(prefix="/api/tradecase", tags=["tradecase"])
Kind = Literal["OWNER", "SKU", "RECIPIENT", "ORDER", "TRIP"]
Warehouse = Path(gt=0)


def tradecase_documents() -> TradecaseDocuments:
    raise RuntimeError("TRADECASE documents are not wired")


@router.get("/warehouses/{warehouse_id}/site")
def site(warehouse_id: int = Warehouse, user: AdminUser = Depends(get_current_user),
         service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.site(warehouse_id, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.put("/warehouses/{warehouse_id}/site")
def configure(body: TradeSiteSetting, warehouse_id: int = Warehouse,
              user: AdminUser = Depends(get_current_user),
              service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.configure(warehouse_id, body, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.post("/messages")
def receive(body: TradeEnvelope, user: AdminUser = Depends(get_current_user),
            service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.receive(body, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("/warehouses/{warehouse_id}/documents/{kind}")
def documents(kind: Kind, warehouse_id: int = Warehouse,
              after: str = Query(default="", max_length=100), limit: int = Query(default=50, ge=1, le=100),
              user: AdminUser = Depends(get_current_user),
              service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.documents(warehouse_id, kind, after, limit, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("/warehouses/{warehouse_id}/documents/{kind}/{external_id:path}")
def document(kind: Kind, external_id: str, warehouse_id: int = Warehouse,
             user: AdminUser = Depends(get_current_user),
             service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    if not 1 <= len(external_id) <= 100:
        raise HTTPException(422, "Invalid document identifier")
    try:
        return service.document(warehouse_id, kind, external_id, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("/warehouses/{warehouse_id}/messages")
def messages(warehouse_id: int = Warehouse, after: str = Query(default="", max_length=100),
             limit: int = Query(default=50, ge=1, le=100), user: AdminUser = Depends(get_current_user),
             service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.messages(warehouse_id, after, limit, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc


@router.get("/warehouses/{warehouse_id}/messages/{event_id}")
def message(event_id: str = Path(min_length=1, max_length=100), warehouse_id: int = Warehouse,
            user: AdminUser = Depends(get_current_user),
            service: TradecaseDocuments = Depends(tradecase_documents)) -> dict[str, Any]:
    try:
        return service.message(warehouse_id, event_id, user.username)
    except TradecaseError as exc:
        raise HTTPException(exc.status, {"code": exc.code}) from exc
