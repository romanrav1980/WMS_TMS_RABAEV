"""Aggregate proven corrective receipts without re-crediting original shipment."""
from decimal import Decimal
from typing import Any


def combine_receipts(receipts: list[dict[str,Any]],total: Decimal) -> dict[str,Any]:
    identities={(r["actual_final_load_operation_id"],r["lot_uid"],r["receipt_operation"])for r in receipts}
    if len(identities)!=len(receipts):
        raise ValueError("DELIVERY_DUPLICATE_RECEIPT_LINE")
    initial=[r for r in receipts if not r.get("is_corrective_receipt",False)]
    corrective=[r for r in receipts if r.get("is_corrective_receipt",False)]
    if len(initial)>1:
        raise ValueError("DELIVERY_MULTIPLE_INITIAL_RECEIPTS")
    histories={Decimal(r.get("confirmed_transport_shortage","0"))for r in receipts}
    recoveries={Decimal(r.get("recovered_transport_quantity","0"))for r in receipts}
    anchors={Decimal(r.get("initial_shipped_quantity",r["shipped"]))for r in receipts}
    loss_ids={r.get("transport_shortage_operation_id")for r in receipts}
    if len(histories)!=1 or len(recoveries)!=1 or len(anchors)!=1 or len(loss_ids)!=1:
        raise ValueError("DELIVERY_CORRECTIVE_ORIGINAL_ACCOUNTING_CONFLICT")
    historical=next(iter(histories));recovered=next(iter(recoveries));anchor=next(iter(anchors))
    if historical<0 or recovered<0 or recovered>historical or anchor+historical!=total:
        raise ValueError("DELIVERY_RECEIPT_ORIGINAL_QUANTITY_CONFLICT")
    corrective_shipped=sum((Decimal(r["shipped"])for r in corrective),Decimal(0))
    if corrective and (None in loss_ids or corrective_shipped>recovered):
        raise ValueError("DELIVERY_CORRECTIVE_RECOVERY_PROOF_REQUIRED")
    if initial and Decimal(initial[0]["shipped"])!=anchor:
        raise ValueError("DELIVERY_INITIAL_RECEIPT_QUANTITY_CONFLICT")
    actual=sum((Decimal(r["shipped"])for r in receipts),Decimal(0))
    if actual>total:
        raise ValueError("DELIVERY_RECEIPTS_EXCEED_ORIGINAL_SHIPMENT")
    result={key:sum((Decimal(r[key])for r in receipts),Decimal(0))for key in ("accepted","missing","refused","damaged")}
    if any(value<0 for value in result.values())or sum(result.values(),Decimal(0))!=actual:
        raise ValueError("DELIVERY_RECEIPT_DISPOSITIONS_QUANTITY_CONFLICT")
    result.update(shipped=actual,unreceived=total-actual,confirmed_transport_shortage=historical-recovered,
                  historical_transport_shortage=historical,recovered_transport_quantity=recovered,
                  open_case_ids={r["receipt_operation"]for r in receipts if r["case_status"]in {"OPEN","ASSIGNED"}})
    return result
