import xml.etree.ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool

from ....auth import AdminUser, require_permission
from ..application.ingestion import IdocConflict
from ..domain.artmas import MAX_IDOC_BYTES
from ..application.receipt_ports import SupplyPort as SupplyOrders

router = APIRouter(prefix="/api/integrations/sap/supply-orders", tags=["sap-supply"])


def supply_service() -> SupplyOrders:
    raise RuntimeError("SAP supply service is not wired")


@router.post("", status_code=202)
async def import_supply(request: Request,
                        user: AdminUser = Depends(require_permission("sap_supply_import")),
                        service: SupplyOrders = Depends(supply_service)) -> dict:
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_IDOC_BYTES:
            raise HTTPException(413, "Supply XML exceeds 4 MiB")
        raw.extend(chunk)
    try:
        return await run_in_threadpool(service.receive, bytes(raw), user.username)
    except IdocConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except (ValueError, ET.ParseError, UnicodeDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("")
def list_supplies(warehouse_id: int | None = None, limit: int = Query(100, ge=1, le=200),
                  user: AdminUser = Depends(require_permission("sap_supply_view")),
                  service: SupplyOrders = Depends(supply_service)) -> list[dict]:
    return service.list(warehouse_id, limit)


@router.get("/by-receipt-document/{document_id}")
def supply_by_document(document_id: int,
                       user: AdminUser = Depends(require_permission("sap_supply_view")),
                       service: SupplyOrders = Depends(supply_service)) -> dict:
    if document_id < 1:
        raise HTTPException(422, "Положительный номер накладной обязателен")
    try:
        return service.by_receipt_document(document_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/{order_id}")
def supply_detail(order_id: str, user: AdminUser = Depends(require_permission("sap_supply_view")),
                  service: SupplyOrders = Depends(supply_service)) -> dict:
    try:
        return service.get(order_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
