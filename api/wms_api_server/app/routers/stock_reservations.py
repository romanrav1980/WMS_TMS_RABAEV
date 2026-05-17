from fastapi import APIRouter, Depends, HTTPException

from ..auth import (
    AdminUser,
    STOCK_RESERVATION_EDIT_PERMISSION,
    STOCK_RESERVATION_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    IdResponse,
    StockReservationCreateRequest,
    StockReservationPromoteRequest,
    StockReservationStatusRequest,
)
from ..services.stock_reservation_service import StockReservationService

router = APIRouter(prefix="/api/stock-reservations", tags=["stock-reservations"])


@router.get("")
def list_stock_reservations(
    reservation_kind: str | None = None,
    reservation_domain: str | None = None,
    status: str | None = None,
    source_doc_type: str | None = None,
    source_doc_id: int | None = None,
    articul: str | None = None,
    ware_id: int | None = None,
    cell: str | None = None,
    uid_pallet: str | None = None,
    batch_id: str | None = None,
    production_order_id: int | None = None,
    pick_plan_id: int | None = None,
    pick_wave_id: int | None = None,
    only_active: int | None = None,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)),
) -> list[dict]:
    return StockReservationService().list_reservations(
        reservation_kind=reservation_kind,
        reservation_domain=reservation_domain,
        status=status,
        source_doc_type=source_doc_type,
        source_doc_id=source_doc_id,
        articul=articul,
        ware_id=ware_id,
        cell=cell,
        uid_pallet=uid_pallet,
        batch_id=batch_id,
        production_order_id=production_order_id,
        pick_plan_id=pick_plan_id,
        pick_wave_id=pick_wave_id,
        only_active=only_active,
        limit=limit,
    )


@router.get("/{reservation_id}")
def get_stock_reservation(
    reservation_id: int,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)),
) -> dict:
    row = StockReservationService().get_reservation(reservation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return row


@router.post("", response_model=IdResponse)
def create_stock_reservation(
    request: StockReservationCreateRequest,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION)),
) -> IdResponse:
    try:
        reservation_id = StockReservationService().create_reservation(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return IdResponse(id=reservation_id)


@router.post("/{reservation_id}/promote-to-hard")
def promote_stock_reservation_to_hard(
    reservation_id: int,
    request: StockReservationPromoteRequest,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION)),
) -> dict[str, str]:
    service = StockReservationService()
    try:
        service.promote_to_hard(reservation_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok"}


@router.post("/{reservation_id}/release")
def release_stock_reservation(
    reservation_id: int,
    request: StockReservationStatusRequest,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION)),
) -> dict[str, str]:
    try:
        StockReservationService().release_reservation(reservation_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok"}


@router.post("/{reservation_id}/consume")
def consume_stock_reservation(
    reservation_id: int,
    request: StockReservationStatusRequest,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION)),
) -> dict[str, str]:
    try:
        StockReservationService().consume_reservation(reservation_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok"}


@router.post("/{reservation_id}/cancel")
def cancel_stock_reservation(
    reservation_id: int,
    request: StockReservationStatusRequest,
    _user: AdminUser = Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION)),
) -> dict[str, str]:
    try:
        StockReservationService().cancel_reservation(reservation_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok"}
