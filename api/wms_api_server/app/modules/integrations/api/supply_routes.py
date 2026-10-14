import xml.etree.ElementTree as ET
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool

from ...platform.public import AdminUser, require_permission
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
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except (ValueError, ET.ParseError, UnicodeDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("")
def list_supplies(warehouse_id: int | None = None, limit: int = Query(100, ge=1, le=200),
                  user: AdminUser = Depends(require_permission("sap_supply_view")),
                  service: SupplyOrders = Depends(supply_service)) -> list[dict]:
    try:
        return service.list(warehouse_id, limit, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc


@router.get("/by-receipt-document/{document_id}")
def supply_by_document(document_id: int,
                       user: AdminUser = Depends(require_permission("sap_supply_view")),
                       service: SupplyOrders = Depends(supply_service)) -> dict:
    if document_id < 1:
        raise HTTPException(422, "Положительный номер накладной обязателен")
    try:
        return service.by_receipt_document(document_id, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/{order_id}")
def supply_detail(order_id: str, user: AdminUser = Depends(require_permission("sap_supply_view")),
                  service: SupplyOrders = Depends(supply_service)) -> dict:
    try:
        return service.get(order_id, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


class PalletPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_number: str = Field(min_length=1, max_length=20)
    pallet_count: int | None = Field(default=None, strict=True, ge=1, le=200)
    quantities: list[Decimal] | None = Field(default=None, min_length=1, max_length=200)
    quantity_step: Decimal | None = Field(default=None, gt=0, decimal_places=6)
    expected_source_signature: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


@router.post("/{order_id}/pallet-plan")
def supply_pallet_plan(order_id: str, body: PalletPlan,
                       user: AdminUser = Depends(require_permission("sap_supply_view")),
                       service: SupplyOrders = Depends(supply_service)) -> dict:
    try:
        return service.pallet_plan(order_id, body.model_dump(mode="json", exclude_none=True), user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/{order_id}/receipt-history")
def history(order_id: str, limit: int=Query(50,ge=1,le=100),
            after_operation: str | None=Query(None,min_length=1,max_length=100),
            user: AdminUser=Depends(require_permission("sap_supply_view")),
            service: SupplyOrders=Depends(supply_service)) -> dict:
    try:
        return service.receipt_history(order_id,limit,after_operation,user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc))from exc
    except LookupError as exc:
        raise HTTPException(404,str(exc))from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc))from exc
