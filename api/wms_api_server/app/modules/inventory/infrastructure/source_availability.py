"""Read-only bounded preview of the exact Oracle source rule; no Python copy of eligibility."""
from decimal import Decimal
from typing import Any
from ....oracle_gateway import OracleGateway


class SourceAvailability:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def list_sources(self, warehouse: int, article: str, quantity: Decimal, purpose: str,
                     min_days: int | None, min_percent: Decimal | None,
                     after_uid: str, after_cell: str, limit: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all("""
            select s.UID_POLETA PALLET_IDENTIFIER,s.CELL,c.WARE_ID,p.ARTICUL,
             to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,
             to_char(s.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY,
             to_char(s.REMAIN-s.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FREE_QTY,
             s.BASE_UOM,s.STOCK_VERSION,p.EXPIRY_DATE,
             RRL_STOCK_ELIGIBILITY.reason(s.UID_POLETA,s.CELL,:ware,:qty,:days,:percent,:purpose,null,p.ARTICUL) REASON_CODE
            from RRL_PALLETS p join RRL_REMAINS s on s.UID_POLETA=p.UID_PALLET
             join RRL_CELLS c on c.CELL=s.CELL
            where p.ARTICUL=:article and c.WARE_ID=:ware
             and (:after_uid is null or s.UID_POLETA>:after_uid or (s.UID_POLETA=:after_uid and s.CELL>:after_cell))
            order by s.UID_POLETA,s.CELL fetch first :bound rows only
        """, {"ware": warehouse, "article": article, "qty": quantity, "days": min_days,
              "percent": min_percent, "purpose": purpose, "after_uid": after_uid or None,
              "after_cell": after_cell or None, "bound": limit + 1})
        page = rows[:limit]
        for row in page:
            row["eligible"] = row["reason_code"] is None
        last = page[-1] if len(rows) > limit else None
        return {"items": page, "next": {"after_uid": last["pallet_identifier"], "after_cell": last["cell"]} if last else None,
                "quantity": format(quantity, "f"), "purpose": purpose, "preview": True}
