from typing import Any

# Лёгкие опции складов для селекторов: только ID/NAME/PARENT_WARE_ID, без подсчёта ячеек и остатков
# (полный /api/admin/warehouses сохраняется для экранов, которым нужны счётчики). Keyset по ID, до 100 строк.
_OPTIONS = """select w.ID,w.NAME,w.PARENT_WARE_ID from RRL_WARES w
 where(:pattern is null or upper(w.NAME) like :pattern escape '!' or to_char(w.ID) like :pattern escape '!')
   and(:after is null or w.ID>:after)
 order by w.ID fetch first :fetch rows only"""


def _pattern(query: str | None) -> str | None:
    text = (query or "").strip().upper()
    if not text:
        return None
    return "%" + text.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"


class WarehouseOptions:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def list(self, query: str | None, after: int | None, limit: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(_OPTIONS, {"pattern": _pattern(query), "after": after, "fetch": limit + 1})
        items = rows[:limit]
        return {"items": items, "next_after": items[-1]["id"] if len(rows) > limit and items else None}
