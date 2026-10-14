"""Bounded immutable norm versions under current warehouse permission."""
from hashlib import sha256
from typing import Any
from ...platform.public import read_oracle_json
from .cost_access import require_warehouse


def read_rate_history(gateway: Any, ware: int, currency: str, before: int,
                      limit: int, actor: str) -> dict[str, Any]:
    key = sha256(f"{ware}:WAREHOUSE_PICKING:{currency}".encode()).hexdigest()
    with gateway.transaction("Current warehouse immutable norm history") as cur:
        cur.execute("set transaction read only")
        require_warehouse(cur, ware, actor, "transport_dispatch_view")
        cur.execute("""
            select h.VERSION_NO,to_char(h.RATE_VALUE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') RATE_VALUE,
              to_char(h.EFFECTIVE_FROM,'YYYY-MM-DD') EFFECTIVE_FROM,h.BASIS,
              h.REASON_TEXT,h.DECISION_REFERENCE,h.ACTOR,h.COMPONENTS_JSON
            from RRL_LOGISTICS_RATE_HEAD head join RRL_LOGISTICS_RATE_HISTORY h on h.RATE_KEY=head.RATE_KEY
            where head.RATE_KEY=:rate_key and head.WARE_ID=:ware and head.CURRENCY=:currency
              and(:before_version=0 or h.VERSION_NO<:before_version)
            order by h.VERSION_NO desc fetch first :row_limit rows only
        """, rate_key=key, ware=ware, currency=currency, before_version=before, row_limit=limit+1)
        columns = [x[0].lower() for x in cur.description]
        values = cur.fetchall()
        rows = []
        for value in values[:limit]:
            row = dict(zip(columns, value))
            wire = row.pop("components_json")
            row["components"] = read_oracle_json(wire) if wire is not None else None
            rows.append(row)
        return {"warehouse_id": ware, "currency": currency, "rows": rows,
                "next_before_version": rows[-1]["version_no"] if len(values)>limit else None}
