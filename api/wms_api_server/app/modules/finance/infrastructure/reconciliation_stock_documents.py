"""Bounded conflicting stock keys; counters and samples share the read-only snapshot."""
import json
from typing import Any
from .reconciliation_stock import COMPOSITION_SOURCE, INVALID_QUANTITY

SOURCES={
    "stock_quantity_invariants": "from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL "
        "where c.WARE_ID=:ware and("+INVALID_QUANTITY+")",
    "physical_unit_composition": COMPOSITION_SOURCE,
}


def stock_documents(cursor: Any,ware: int,counts: dict[str,int]) -> dict[str,Any]:
    parts=[]
    result={}
    for key,source in SOURCES.items():
        if not counts.get(key):continue
        result[key]={"available":True,"metric":key,"document_kind":"STOCK_ROW","document_ids":[],
                     "stock_rows":[],"limit":20,"has_more":counts[key]>20,
                     "scope":"CURRENT_STOCK_SNAPSHOT"}
        parts.append("select '"+key+"' METRIC,UID_PALLET,CELL,BASE_UOM,PHYSICAL,HARD from "
            "(select cast(r.UID_POLETA as varchar2(200)) UID_PALLET,r.CELL,r.BASE_UOM,"
            "to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL,"
            "to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD "
            +source+" order by r.UID_POLETA,r.CELL fetch first 20 rows only)")
    if parts:
        cursor.execute(" union all ".join(parts),ware=ware)
        for key,uid,cell,uom,physical,hard in cursor.fetchall():
            identifier=json.dumps([uid,cell],ensure_ascii=False,separators=(",",":"))
            result[key]["document_ids"].append(identifier)
            result[key]["stock_rows"].append({"document_id":identifier,"uid_pallet":uid,
                "cell":cell,"base_uom":uom,"physical_quantity":physical,"hard_quantity":hard})
    return result