"""Exact original-owner credit; no proportional guess for a shared partial leaf."""
from collections import defaultdict
from decimal import Decimal
from typing import Any
from .receipt_totals import combine_receipts

FIELDS=("accepted","missing","refused","damaged")
def text(value: Decimal) -> str:
    return format(value,"f").rstrip("0").rstrip(".") if "." in format(value,"f") else format(value,"f")


def project_delivery(order_id: int,legs: list[dict[str,Any]],fulfillments: list[dict[str,Any]],receipts: list[dict[str,Any]]) -> dict[str,Any]:
    original_sources={(leg["shipping_operation"],leg["shipment_id"]) for leg in legs if leg["owner_order_id"]==order_id}
    if any(row["status"]=="SHIPPED" and (row["shipping_operation"],row["shipment_id"]) not in original_sources for row in fulfillments):
        raise ValueError("DELIVERY_ORIGINAL_OWNER_PROVENANCE_REQUIRED")
    contexts={row["shipment_id"]:row for row in fulfillments if row["status"]=="SHIPPED"}
    by_load_uid:dict[tuple[str,str],list[dict[str,Any]]]=defaultdict(list)
    for row in receipts:
        by_load_uid[(row["load_operation_id"],row.get("original_lot_uid",row["lot_uid"]))].append(row)
    grouped:dict[tuple[str,str],list[dict[str,Any]]]=defaultdict(list)
    for leg in legs:
        grouped[(leg["shipping_operation"],leg["lot_uid"])].append(leg)
    totals:dict[tuple[str,str],dict[str,Decimal]]={}
    unresolved=[];places=set();open_cases=set()
    for (operation,uid),members in grouped.items():
        owned=[leg for leg in members if leg["owner_order_id"]==order_id]
        if not owned:
            continue
        identity={(leg["article"],leg["base_uom"]) for leg in members}
        if len(identity)!=1:
            raise ValueError("DELIVERY_ORIGINAL_LEAF_IDENTITY_CONFLICT")
        article,unit=next(iter(identity))
        total=sum((Decimal(leg["quantity"]) for leg in members),Decimal(0))
        owned_total=sum((Decimal(leg["quantity"]) for leg in owned),Decimal(0))
        contexts_owned=[contexts.get(leg["shipment_id"]) for leg in owned]
        if any(row is None or row["shipping_operation"]!=operation for row in contexts_owned):
            raise ValueError("DELIVERY_FULFILLMENT_ORIGINAL_SOURCE_CONFLICT")
        loads={row["load_operation_id"] for row in contexts_owned}
        if len(loads)!=1:
            raise ValueError("DELIVERY_LEAF_PHYSICAL_LOAD_CONFLICT")
        load=next(iter(loads));receipt=by_load_uid.get((load,uid)) if load else None
        counter=totals.setdefault((article,unit),{key:Decimal(0) for key in ("shipped",*FIELDS,"unreceived","unattributed","confirmed_transport_shortage","historical_transport_shortage","recovered_transport_quantity")})
        counter["shipped"]+=owned_total
        if load:
            places.add(load)
        if not receipt:
            counter["unreceived"]+=owned_total
            continue
        combined=combine_receipts(receipt,total)
        open_cases.update(combined["open_case_ids"])
        owners={leg["owner_order_id"] for leg in members}
        if len(owners)==1:
            counter["confirmed_transport_shortage"]+=combined["confirmed_transport_shortage"]
            counter["historical_transport_shortage"]+=combined["historical_transport_shortage"]
            counter["recovered_transport_quantity"]+=combined["recovered_transport_quantity"]
            counter["unreceived"]+=combined["unreceived"]
            for field in FIELDS:
                counter[field]+=combined[field]
        elif combined["accepted"]==total:
            counter["accepted"]+=owned_total
        else:
            counter["unattributed"]+=owned_total
            unresolved.append({"shipping_operation":operation,"load_operation_id":load,"lot_uid":uid,"original_owner_ids":sorted(owner for owner in owners if owner is not None),
                               "reason":"SHARED_PARTIAL_LEAF_REQUIRES_EXPLICIT_OWNER_ALLOCATION"})
    unshipped=sum(row["status"] not in {"SHIPPED","CANCELLED"} for row in fulfillments)
    if unresolved:
        status="NEEDS_OWNER_ALLOCATION"
    elif any(value["unreceived"]>value["confirmed_transport_shortage"] for value in totals.values()):
        status="WAITING_FOR_RECEIPT"
    elif any(any(value[field]>0 for field in ("missing","refused","damaged","confirmed_transport_shortage")) for value in totals.values()):
        status="PARTIALLY_ACCEPTED"
    elif open_cases:
        status="ACCEPTED_WITH_OPEN_CASE"
    elif totals:
        status="RECEIVED_SHIPPED_VOLUME"
    else:
        status="WAITING_FOR_SHIPMENT"
    return {"customer_order_id":order_id,"delivery_status":status,"unshipped_fulfillments":unshipped,
            "delivery_scope":"SHIPPED_VOLUME","physical_place_count":len(places),"open_case_ids":sorted(open_cases),"needs_owner_allocation":unresolved,
            "quantities":[{"article":article,"base_uom":unit,**{key:text(value) for key,value in counter.items()}} for (article,unit),counter in sorted(totals.items())]}
