"""
export_1c.py — Экспорт биллинг-заказов в формат 1С CommerceML.

Sprint 113.
"""

import xml.etree.ElementTree as ET
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from ..auth import AdminUser, BILLING_EDIT_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/transport/billing", tags=["billing-1c"])


def _gw() -> OracleGateway:
    return OracleGateway()


def _build_1c_xml(orders: list[dict]) -> bytes:
    root = ET.Element("КоммерческаяИнформация", {"Версия": "2.09", "ДатаФормирования": str(date.today())})
    for o in orders:
        doc = ET.SubElement(root, "Документ")
        ET.SubElement(doc, "Ид").text = str(o.get("id") or "")
        ET.SubElement(doc, "Номер").text = str(o.get("num") or o.get("id") or "")
        ET.SubElement(doc, "Дата").text = str(o.get("dateoforder") or "")[:10]
        ET.SubElement(doc, "Контрагент").text = str(o.get("company") or "")
        ET.SubElement(doc, "Статус").text = (
            "Оплачен" if o.get("payed") else "Закрыт" if o.get("closed") else "Выставлен"
        )
        amount_el = ET.SubElement(doc, "Сумма")
        amount_el.text = str(o.get("total_amount") or "0")
        tasks_el = ET.SubElement(doc, "Табличная")
        for t in o.get("tasks", []):
            row = ET.SubElement(tasks_el, "Строка")
            ET.SubElement(row, "Рейс").text = str(t.get("tt_id") or "")
            ET.SubElement(row, "Маршрут").text = str(t.get("transport") or "")
            ET.SubElement(row, "Дата").text = str(t.get("shipment_date") or "")[:10]
            ET.SubElement(row, "Сумма").text = str(t.get("price") or "0")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


@router.get("/orders/{order_id}/export/1c")
def export_order_1c(
    order_id: int,
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> Response:
    """Экспорт счёта в XML формат 1С CommerceML (Sprint 113)."""
    gw = _gw()
    order_rows = gw.fetch_all(
        """
        SELECT B.ID, B.NUM, B.COMPANY, B.DATEOFORDER, B.CLOSED, B.PAYED,
               SUM(NVL(TT.PRICE,0)) AS TOTAL_AMOUNT
          FROM RABAEV.RRL_BILL_ORDERS B
          LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.PAY_ORDER_ID = B.ID AND NVL(TT.DELETED,0)=0
         WHERE B.ID = :oid
         GROUP BY B.ID, B.NUM, B.COMPANY, B.DATEOFORDER, B.CLOSED, B.PAYED
        """,
        {"oid": order_id},
    )
    if not order_rows:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    task_rows = gw.fetch_all(
        "SELECT ID AS TT_ID, TRANSPORT, SHIPMENT_DATE, PRICE FROM RABAEV.RRL_TRANSPORT_TASK WHERE PAY_ORDER_ID=:oid AND NVL(DELETED,0)=0",
        {"oid": order_id},
    )
    order = {str(k).lower(): v for k, v in order_rows[0].items()}
    order["tasks"] = [{str(k).lower(): v for k, v in t.items()} for t in task_rows]
    xml_bytes = _build_1c_xml([order])
    fname = f"billing_order_{order_id}.xml"
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/orders/export/1c")
def export_orders_1c(
    date_from: date = Query(...),
    date_to: date = Query(...),
    status: str | None = Query(default=None),
    _user: AdminUser = Depends(require_permission(BILLING_EDIT_PERMISSION)),
) -> Response:
    """Реестр счетов в XML формат 1С (Sprint 113)."""
    gw = _gw()
    where = "WHERE TRUNC(B.DATEOFORDER) BETWEEN :d1 AND :d2"
    params: dict = {"d1": date_from, "d2": date_to}
    if status == "paid":
        where += " AND B.PAYED=1"
    elif status == "closed":
        where += " AND B.CLOSED=1 AND NVL(B.PAYED,0)=0"
    order_rows = gw.fetch_all(
        f"""
        SELECT B.ID, B.NUM, B.COMPANY, B.DATEOFORDER, B.CLOSED, B.PAYED,
               SUM(NVL(TT.PRICE,0)) AS TOTAL_AMOUNT
          FROM RABAEV.RRL_BILL_ORDERS B
          LEFT JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.PAY_ORDER_ID = B.ID AND NVL(TT.DELETED,0)=0
          {where}
         GROUP BY B.ID, B.NUM, B.COMPANY, B.DATEOFORDER, B.CLOSED, B.PAYED
         ORDER BY B.DATEOFORDER
        """,
        params,
    )
    orders = [{str(k).lower(): v for k, v in r.items()} for r in order_rows]
    xml_bytes = _build_1c_xml(orders)
    fname = f"billing_registry_{date_from}_{date_to}.xml"
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
