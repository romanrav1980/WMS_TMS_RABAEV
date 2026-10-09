from fastapi import APIRouter, Depends, HTTPException
from ..auth import AdminUser, get_current_admin, serialize_admin_user

from ..legacy_protocol import encode_legacy_blocks, fault
from ..schemas import (
    CallSpfRequest,
    LegacyBlockModel,
    LegacyExecuteRequest,
    LegacyExecuteResponse,
    LotCheckRequest,
    OrderCheckRequest,
    PlaceCheckRequest,
)
from ..services.tserver_service import TserverService

router = APIRouter(prefix="/api", tags=["tserver"])


def _to_models(blocks) -> list[LegacyBlockModel]:
    return [LegacyBlockModel(function_name=block.function_name, values=block.values) for block in blocks]


def _fault_response(exc: Exception) -> LegacyExecuteResponse:
    blocks = [fault(str(exc))]
    return LegacyExecuteResponse(payload=encode_legacy_blocks(blocks), blocks=_to_models(blocks))


@router.post("/legacy/tserver/execute", response_model=LegacyExecuteResponse)
def execute_legacy_tserver(request: LegacyExecuteRequest, user: AdminUser = Depends(get_current_admin)) -> LegacyExecuteResponse:
    payload, blocks = TserverService().execute_legacy_payload(request.payload, user.username)
    return LegacyExecuteResponse(payload=payload, blocks=_to_models(blocks))


@router.get("/terminal/users/{user_id}", response_model=list[LegacyBlockModel])
def get_terminal_user(user_id: str) -> list[LegacyBlockModel]:
    try:
        return _to_models(TserverService().get_ruser(user_id))
    except Exception as exc:
        return _to_models([fault(str(exc))])


@router.get("/products/by-barcode/{barcode}", response_model=list[LegacyBlockModel])
def get_product_by_barcode(barcode: str) -> list[LegacyBlockModel]:
    try:
        return _to_models(TserverService().get_product_info(barcode))
    except Exception as exc:
        return _to_models([fault(str(exc))])


@router.get("/lots/{usscc}/items", response_model=LegacyExecuteResponse)
def get_lot_items(usscc: str) -> LegacyExecuteResponse:
    try:
        blocks = TserverService().get_lot_items(usscc)
        return LegacyExecuteResponse(payload=encode_legacy_blocks(blocks), blocks=_to_models(blocks))
    except Exception as exc:
        return _fault_response(exc)


@router.get("/places/{place_id}/items", response_model=LegacyExecuteResponse)
def get_place_items(place_id: str) -> LegacyExecuteResponse:
    try:
        blocks = TserverService().get_place_items(place_id)
        return LegacyExecuteResponse(payload=encode_legacy_blocks(blocks), blocks=_to_models(blocks))
    except Exception as exc:
        return _fault_response(exc)


@router.post("/terminal/lots/{usscc}/check")
def confirm_lot_check(usscc: str, request: LotCheckRequest, user: AdminUser = Depends(get_current_admin)) -> dict[str, str]:
    request.user_id = user.username
    try:
        TserverService().confirm_lot_check(usscc, request)
    except ValueError as error:
        raise HTTPException(422, detail={"code": "QUALITY_REQUEST_INVALID", "message": str(error),
            "operation_id": request.operation_id, "outcome_confirmed": False}) from error
    return {"status": "ok", "legacy_func": "END_LOT_CHECK_PASSED"}


@router.post("/terminal/place-checks")
def confirm_place_check(request: PlaceCheckRequest) -> dict[str, str]:
    TserverService().confirm_place_check(request)
    return {"status": "ok", "legacy_func": "END_PALLET_CHECK_PASSED"}


@router.post("/terminal/order-checks")
def confirm_order_check(request: OrderCheckRequest) -> dict[str, str]:
    result = TserverService().confirm_order_check(request)
    return {"status": "ok", "legacy_func": "END_ORDER_CHECK_PASSED", **result}


@router.post("/terminal/call-spf")
def call_spf(request: CallSpfRequest, user: AdminUser = Depends(get_current_admin)) -> dict[str, str]:
    result = TserverService().call_spf(request, user.username)
    return {"ok": result}


@router.get("/terminal/auth/me")
def terminal_identity(user: AdminUser = Depends(get_current_admin)) -> dict:
    return serialize_admin_user(user)
