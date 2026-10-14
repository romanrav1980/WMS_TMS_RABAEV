"""SAP receipt entry point for the sole stock posting coordinator."""
from decimal import Decimal
from typing import Any
from ..contracts_stock import StockCommand,StockPostingError
from .stock_posting_uow import StockPosting

def receive_command(gateway: Any, order_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
    rows = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not rows or rows[0]["state"] != "ACTIVE":
        raise StockPostingError("STOCK_RELEASE_NOT_ACTIVE",payload["operation_id"])
    metadata = {k: v for k, v in payload.items() if k != "operation_id" and not (k in {"capture_mode", "policy_version", "weighted_boxes"} and v is None)}
    metadata["quantity"] = format(Decimal(str(payload["quantity"])), "f")
    # Decimal fields must reach JSON as exact strings.
    for name in ("gross_weight", "pallet_height", "pallet_height_m", "volume_m3"):
        if isinstance(metadata.get(name), Decimal):
            metadata[name] = format(metadata[name], "f")
    return StockPosting().post(StockCommand(operation_id=payload["operation_id"], command_type="SAP_RECEIPT",
        actor=actor, lines=(), source={"type": "SAP_SUPPLY_ORDER", "order_id": order_id}, metadata=metadata))
