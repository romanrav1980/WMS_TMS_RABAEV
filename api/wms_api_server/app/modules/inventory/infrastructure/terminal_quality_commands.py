"""Terminal quality/audit facts enter posting before legacy metadata DML."""
from datetime import datetime
from ..contracts_stock import StockCommand
from ..domain.stock_quantity import quantity_text
from .stock_posting_uow import StockPosting


def post_terminal_quality(gateway, pallet: str, request):
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if state and state[0]["state"] == "PREPARED":
        return None
    if not request.operation_id or not request.user_id:
        raise ValueError("Authenticated actor and persistent operation_id required")
    errors, checked = [], []
    for item in request.errors:
        if item.usscc and item.usscc != pallet:
            raise ValueError("Quality command cannot edit another pallet")
        errors.append({"article": item.uid, "quantity": quantity_text(item.qty), "condition": item.condition})
    for item in request.vp_lines:
        if item.pallet_uid != pallet:
            raise ValueError("Quality command cannot edit another pallet")
        stamp = item.checked_at
        if isinstance(stamp, str):
            try:
                stamp = datetime.strptime(stamp, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                stamp = datetime.fromisoformat(stamp)
        checked.append({"article": item.uid, "checked_at": stamp.strftime("%Y-%m-%d %H:%M:%S")})
    return StockPosting().post(StockCommand(
        operation_id=request.operation_id, command_type="OUTGOING_PALLET_CHECK", actor=request.user_id,
        source={"pallet_identifier": pallet}, lines=(), metadata={"quality_kind": "SCAN",
            "error_count": request.error_count, "note": None, "picker": request.user_id,
            "terminal_audit": {"errors": errors, "vp_lines": checked}}))
