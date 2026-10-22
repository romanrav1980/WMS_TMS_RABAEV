"""Bounded deferred intake; the native document owner decides and journals every result."""
from typing import Any

import oracledb

from ...platform.public import read_oracle_json
from ..contracts_tradecase import TradecaseError
from .tradecase_documents import native_error


class TradeDeferredWorker:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def reconcile(self, warehouse: int, actor: str, limit: int = 25) -> dict[str, Any]:
        if isinstance(warehouse, bool) or not isinstance(warehouse, int) or warehouse < 1:
            raise ValueError("A positive warehouse is required")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 25:
            raise ValueError("Batch limit must be between 1 and 25")
        if not actor or len(actor) > 50:
            raise ValueError("An existing service actor is required")
        report = dict(warehouse_id=warehouse, status="OK", processed=0, accepted=0, rejected=0, waiting=0)
        try:
            with self.gateway.transaction("TRADECASE deferred document worker") as cur:
                # Same order as native document intake: access revision, then site, then deferred rows.
                cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
                for permission in ("tradecase_import", "tradecase_view"):
                    cur.callproc("RRL_ACCESS_API.assert_allowed", [actor, permission, "WAREHOUSE", str(warehouse)])
                cur.execute("select SOURCE_ID,ENABLED from RRL_TRADE_SITE where WARE_ID=:w for update skip locked", w=warehouse)
                site = cur.fetchone()
                if site is None:
                    # A locked site and an absent site produce no commands; do not wait behind another worker.
                    return dict(report, status="UNAVAILABLE")
                source, enabled = site
                if enabled != 1:
                    raise TradecaseError("SITE_DISABLED", 409)
                cur.execute("""
                    select d.EVENT_ID from RRL_TRADE_DEFERRED d
                    join RRL_TRADE_MESSAGE m on m.WARE_ID=d.WARE_ID
                     and m.SOURCE_ID=d.SOURCE_ID and m.EVENT_ID=d.EVENT_ID
                    where d.WARE_ID=:w and d.SOURCE_ID=:s and d.STATE='WAITING'
                     and (nvl(json_value(m.REQUEST_JSON,'$.payload.order_kind'),'OUTBOUND')<>'BUYOUT'
                      or RRL_ACCESS_API.allowed(:actor,'tradecase_buyout_basis_import','WAREHOUSE',:scope)=1)
                    order by d.ATTEMPTS,d.CHANGED_AT,d.EVENT_ID fetch first :n rows only
                    """, w=warehouse, s=source, actor=actor, scope=str(warehouse), n=limit)
                events = [row[0] for row in cur.fetchall()]
                for event in events:
                    output = cur.var(oracledb.DB_TYPE_CLOB)
                    cur.callproc("RRL_TRADE_DOCUMENT_API.retry_document", [warehouse, actor, event, output])
                    result = read_oracle_json(output.getvalue())
                    state = str(result.get("status", "")).lower()
                    if state not in {"accepted", "rejected", "waiting"}:
                        raise RuntimeError("Unexpected native deferred result")
                    report[state] += 1
                    report["processed"] += 1
            return report
        except oracledb.DatabaseError as exc:
            raise native_error(exc) from exc
