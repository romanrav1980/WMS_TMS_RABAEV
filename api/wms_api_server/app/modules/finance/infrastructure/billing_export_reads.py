"""One read-only snapshot per legacy billing workbook, with explicit overflow rejection."""
import json
from datetime import date
from typing import Any
from ..contracts_billing_export import BillingExportError
from .billing_export_access import authorize_billing_export

MAX_ORDERS = 2000
MAX_TASKS = 5000
HEADER = """select B.ID order_id,B.NUM num,B.COMPANY company,B.NUM_PLAT num_plat,
    to_char(B.DATEOFORDER,'YYYY-MM-DD') date_of_order,
    to_char(B.DATEFROM,'YYYY-MM-DD') date_from,to_char(B.DATETO,'YYYY-MM-DD') date_to,
    nvl(B.CLOSED,0) closed,nvl(B.PAYED,0) payed from RRL_BILL_ORDERS B"""


def _rows(cursor: Any) -> list[dict[str, Any]]:
    names = [column[0].lower() for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def billing_order_export_rows(gateway: Any, order_id: int, actor: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with gateway.transaction("Bounded billing order export READ ONLY") as cur:
        cur.execute("set transaction read only")
        cur.execute(HEADER + " where B.ID=:order_id", order_id=order_id)
        headers = _rows(cur)
        if not headers:
            raise BillingExportError("BILLING_ORDER_NOT_FOUND", f"Billing order {order_id} not found", 404)
        authorize_billing_export(cur, [order_id], actor)
        cur.execute("""select TT.ID tt_id,TT.TRANSPORT transport,TT.CONDITION status,
            nvl(TT.PRICE,0) price,to_char(TT.SHIPMENT_DATE,'YYYY-MM-DD') shipment_date
            from RRL_TRANSPORT_TASK TT where TT.PAY_ORDER_ID=:order_id
            order by TT.SHIPMENT_DATE,TT.ID fetch first 5001 rows only""", order_id=order_id)
        tasks = _rows(cur)
        if len(tasks) > MAX_TASKS:
            raise BillingExportError("BILLING_EXPORT_TASK_BOUND_5000", "В счёте более 5000 рейсов; разделите счёт для выгрузки")
        for task in tasks:
            task["tt_id"] = int(task["tt_id"])
            task["price"] = float(task["price"] or 0)
        header = headers[0]
        header.update(task_count=len(tasks), total_price=sum(task["price"] for task in tasks))
        return header, tasks


def billing_registry_export_rows(gateway: Any, company: str | None, date_from: date | None,
        date_to: date | None, closed: int | None, payed: int | None, actor: str) -> list[dict[str, Any]]:
    conditions, params = ["1=1"], {}
    if company:
        conditions.append("upper(B.COMPANY) like upper(:company)")
        params["company"] = "%" + company + "%"
    if date_from:
        conditions.append("B.DATEFROM>=to_date(:date_from,'YYYY-MM-DD')")
        params["date_from"] = str(date_from)
    if date_to:
        conditions.append("B.DATETO<=to_date(:date_to,'YYYY-MM-DD')")
        params["date_to"] = str(date_to)
    for name, value in (("closed", closed), ("payed", payed)):
        if value is not None:
            conditions.append("B." + name.upper() + "=:" + name)
            params[name] = value
    query = HEADER + " where " + " and ".join(conditions) + " order by B.ID desc fetch first 2001 rows only"
    with gateway.transaction("Bounded billing registry export READ ONLY") as cur:
        cur.execute("set transaction read only")
        cur.execute(query, params)
        headers = _rows(cur)
        if len(headers) > MAX_ORDERS:
            raise BillingExportError("BILLING_EXPORT_ORDER_BOUND_2000", "Найдено более 2000 счетов; уточните фильтры выгрузки")
        authorize_billing_export(cur, [int(row["order_id"]) for row in headers], actor)
        if not headers:
            return []
        # Group every task of the selected orders; no limit is applied to their monetary totals.
        ids = [int(row["order_id"]) for row in headers]
        cur.execute("""select TT.PAY_ORDER_ID order_id,count(*) task_count,sum(nvl(TT.PRICE,0)) total_price
            from RRL_TRANSPORT_TASK TT join json_table(:ids,'$[*]'columns(id number path '$')) selected
            on selected.id=TT.PAY_ORDER_ID group by TT.PAY_ORDER_ID""", ids=json.dumps(ids))
        totals = {int(row["order_id"]): row for row in _rows(cur)}
        for header in headers:
            values = totals.get(int(header["order_id"]), {})
            header.update(task_count=int(values.get("task_count") or 0), total_price=float(values.get("total_price") or 0))
        return headers
