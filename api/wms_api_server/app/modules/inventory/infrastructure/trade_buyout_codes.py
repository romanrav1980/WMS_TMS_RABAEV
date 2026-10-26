"""Read marking codes only for the native-authorized page of buyout units."""
import json
from typing import Any

import oracledb

from ..contracts_trade_stock import TradeStockError


def attach_buyout_codes(cursor: Any, page: dict[str, Any], warehouse: int, buyout: str) -> dict[str, Any]:
    items = page.get("items", [])
    if not items:
        return page
    if len(items) > 100:
        raise TradeStockError("TRADE_BUYOUT_PAGE_LIMIT", 409)
    keys = list(dict.fromkeys(item["physical_unit_key"] for item in items))
    selected = cursor.var(oracledb.DB_TYPE_CLOB)
    selected.setvalue(0, json.dumps(keys))
    cursor.execute("""select /* TRADE_BUYOUT_PAGE_MARKS */ u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE,
        coalesce(ct.SSCC,u.CURRENT_UID),u.STOCK_STATUS
        from json_table(:selected,'$[*]' columns(PHYSICAL_UNIT_KEY varchar2(64) path '$')) k
        join RRL_TRADE_BUYOUT_UNIT bu on bu.PHYSICAL_UNIT_KEY=k.PHYSICAL_UNIT_KEY and bu.BUYOUT_ID=:buyout
        join RRL_TRADE_BUYOUT b on b.BUYOUT_ID=bu.BUYOUT_ID and b.WARE_ID=:warehouse
        join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=bu.PHYSICAL_UNIT_KEY
        left join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=u.CURRENT_UID
        left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lot.CASE_PICK_TASK_ID
        left join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
        order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH""",
        selected=selected, buyout=buyout, warehouse=warehouse)
    codes: dict[str, list[dict[str, str]]] = {key: [] for key in keys}
    places: dict[str, tuple[str, str]] = {}
    for key, system, raw, carrier, state in cursor:
        places[key] = carrier, state
        if raw is not None:
            codes[key].append({"system_code": system, "code": raw.read() if hasattr(raw, "read") else raw})
    for item in items:
        key = item["physical_unit_key"]
        item["marking_codes"] = codes[key]
        item["carrier_identifier"], item["stock_status"] = places[key]
    return page
