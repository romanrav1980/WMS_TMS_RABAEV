from fastapi import APIRouter

from ..legacy_protocol import encode_legacy_blocks
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


@router.post("/legacy/tserver/execute", response_model=LegacyExecuteResponse)
def execute_legacy_tserver(request: LegacyExecuteRequest) -> LegacyExecuteResponse:
    payload, blocks = TserverService().execute_legacy_payload(request.payload)
    return LegacyExecuteResponse(payload=payload, blocks=_to_models(blocks))


@router.get("/terminal/users/{user_id}", response_model=list[LegacyBlockModel])
def get_terminal_user(user_id: str) -> list[LegacyBlockModel]:
    return _to_models(TserverService().get_ruser(user_id))


@router.get("/products/by-barcode/{barcode}", response_model=list[LegacyBlockModel])
def get_product_by_barcode(barcode: str) -> list[LegacyBlockModel]:
    return _to_models(TserverService().get_product_info(barcode))


@router.get("/lots/{usscc}/items", response_model=LegacyExecuteResponse)
def get_lot_items(usscc: str) -> LegacyExecuteResponse:
    blocks = TserverService().get_lot_items(usscc)
    return LegacyExecuteResponse(payload=encode_legacy_blocks(blocks), blocks=_to_models(blocks))


@router.get("/places/{place_id}/items", response_model=LegacyExecuteResponse)
def get_place_items(place_id: str) -> LegacyExecuteResponse:
    blocks = TserverService().get_place_items(place_id)
    return LegacyExecuteResponse(payload=encode_legacy_blocks(blocks), blocks=_to_models(blocks))


@router.post("/terminal/lots/{usscc}/check")
def confirm_lot_check(usscc: str, request: LotCheckRequest) -> dict[str, str]:
    TserverService().confirm_lot_check(usscc, request)
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
def call_spf(request: CallSpfRequest) -> dict[str, str]:
    result = TserverService().call_spf(request)
    return {"ok": result}
