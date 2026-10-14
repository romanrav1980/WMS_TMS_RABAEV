"""Authoritative current release fence; never opts out to a legacy effect executor."""
from typing import Any
from ..contracts_stock import StockPostingError

def require_active_release(gateway: Any,operation_id: str|None=None) -> None:
    rows=gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not rows or rows[0]["state"]!="ACTIVE":
        raise StockPostingError("STOCK_RELEASE_NOT_ACTIVE",operation_id or "")
