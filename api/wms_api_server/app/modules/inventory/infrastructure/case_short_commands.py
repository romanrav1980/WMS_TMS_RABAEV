"""Existing shortage approval enters the same atomic posting transaction."""
from ..contracts_stock import StockCommand
from .stock_posting_uow import StockPosting


def post_short_approval(gateway, short_id: int, request):
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if state and state[0]["state"] == "PREPARED":
        return None
    if short_id < 1 or not request.actor:
        raise ValueError("Shortage ID and authenticated actor required")
    return StockPosting().post(StockCommand(
        operation_id=request.operation_id or "CASE.SHORT.APPROVE:" + str(short_id),
        command_type="CASE_SHORT_APPROVE", actor=request.actor, lines=(),
        source={"short_id": short_id}, metadata={"reason": request.reason_text}))
