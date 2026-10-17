"""Bound the legacy dispatcher query before aggregation and apply native object scope."""
from datetime import date, timedelta
from typing import Any
from ..contracts_dispatch_read import TripListFilter, DispatchReadError
from .dispatch_read_scope import trip_scope_predicate


def trip_list_filters(f: TripListFilter, actor: str | None = None) -> tuple[str, dict[str, Any]]:
    conditions: list[str] = []
    params: dict[str, Any] = {}
    if not f.include_deleted:
        conditions.append("(TT.DELETED IS NULL OR TT.DELETED=0)")
    start, finish = f.date_from, f.date_to
    if f.shipment_date is not None:
        start, finish = f.shipment_date, f.shipment_date
    elif start is None and finish is None and f.task_id is None:
        finish = date.today()
        start = finish - timedelta(days=31)
    elif start is None and finish is not None:
        start = finish - timedelta(days=31)
    elif start is not None and finish is None:
        finish = start + timedelta(days=31)
    if start is not None and finish is not None and (finish < start or (finish-start).days > 93):
        raise DispatchReadError("TRANSPORT_READ_WINDOW_MAX_93_DAYS", 422)
    if start is not None:
        conditions.append("TT.SHIPMENT_DATE >= :date_from")
        params["date_from"] = start
    if finish is not None:
        conditions.append("TT.SHIPMENT_DATE < :date_to_next")
        params["date_to_next"] = finish + timedelta(days=1)
    for value, expression, key in ((f.condition,"TT.CONDITION=:condition","condition"),
                                    (f.task_id,"TT.ID=:task_id_f","task_id_f")):
        if value is not None:
            conditions.append(expression)
            params[key] = value
    for value, expression, key in ((f.transport_mask,"UPPER(TT.TRANSPORT) LIKE UPPER(:transport_mask)","transport_mask"),
                                   (f.company_mask,"UPPER(NVL(V.DOVERENNOST_OT,'')) LIKE UPPER(:company_mask)","company_mask")):
        if value:
            conditions.append(expression)
            params[key] = "%" + value + "%"
    if f.no_payments_only:
        conditions.append("(TT.PAY_ORDER_ID IS NULL OR TT.PAY_ORDER_ID=0)")
    if actor is not None:
        conditions.append(trip_scope_predicate())
        params["read_actor"] = actor
    return "WHERE " + " AND ".join(conditions) if conditions else "", params
