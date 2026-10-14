"""Readiness of interwarehouse promises only; native departure remains authoritative."""
from decimal import Decimal
from typing import Any

def incoming_readiness(trip_id: int, warehouse_id: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[tuple[str,str],Decimal] = {}
    for row in rows:
        key=(row["article"],row["base_uom"])
        totals[key]=totals.get(key,Decimal(0))+Decimal(row["quantity"])
        row["physically_loaded"] = (
            row["load_status"]in("LOADED","DEPARTED") and row["load_trip_id"]==trip_id
            and row["load_operation_state"]=="APPLIED"
        )
        accounted=row.get("receipt_complete",1)==1 or row.get("shortage_resolved",0)==1
        if "loaded_quantity"in row:
            row["physically_loaded"]=row["physically_loaded"] and row.get("loaded_pallet_identifier")==row.get("received_pallet_identifier") and row.get("loaded_quantity") is not None and row.get("received_quantity") is not None and Decimal(row["loaded_quantity"])==Decimal(row["received_quantity"])
        row["quantity_to_load"]=row.get("received_quantity")if accounted else None
        row["incoming_accounted"]=accounted
        row["ready"] = row["physically_loaded"] and row["temperature_decision"]!="HOLD" and accounted
    return {
        "trip_id":trip_id,"warehouse_id":warehouse_id,"scope":"INTERWARE_EXPECTATIONS_ONLY",
        "expected_deliveries":len(rows),"ready_deliveries":sum(row["ready"] for row in rows),
        "incoming_ready":bool(rows) and all(row["ready"] for row in rows),
        "departure_authorized":False,"plans":rows,
        "expected_quantities":[{"article":a,"base_uom":u,"quantity":format(q,"f")} for (a,u),q in sorted(totals.items())],
    }
