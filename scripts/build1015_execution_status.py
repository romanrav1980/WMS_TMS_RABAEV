from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py";v=read(p)
v=v.replace('base_uom=row["base_uom"])','base_uom=row["base_uom"], requested_uom=row["unit_code"])',1)
v=v.replace('result.update(status=status, reason=reason, requested_quantity=_text(requested), remaining_quantity=_text(remaining))','result.update(status=status, reason=reason, requested_quantity=_text(requested), requested_uom=row["base_uom"], remaining_quantity=_text(remaining))',1)
v+='''

def order_progress_status(lines: list[dict[str, Any]]) -> str:
    """Never hide excess, unresolved units or closed shortage behind PARTIAL."""
    if any(line["status"] == "OVER_PICKED" for line in lines):
        return "OVER_PICKED"
    if any(line["status"] == "REQUIRES_UOM" for line in lines):
        return "REQUIRES_UOM"
    active = [line for line in lines if line["status"] != "CANCELLED"]
    if not active:
        return "CANCELLED" if lines else "PENDING"
    if all(line["status"] == "PICKED" for line in active):
        return "PICKED"
    if any(line["status"] in {"REFUSED", "PARTIAL_REFUSED"} for line in active):
        return ("SHORT_CLOSED" if all(line["status"] in {"PICKED", "REFUSED", "PARTIAL_REFUSED"}
                                      for line in active) else "PARTIAL_REFUSED")
    if any(Decimal(line["picked_quantity"]) > 0 for line in active):
        return "PARTIAL"
    if any(line["status"] == "RESERVED" for line in active):
        return "RESERVED"
    return "PENDING"
'''
files[p]=v
p="api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py";v=read(p)
v=v.replace('from decimal import Decimal\n','',1).replace('from ..domain.execution_progress import line_progress','from ..domain.execution_progress import line_progress, order_progress_status',1)
start=v.index('        complete = bool(lines)');end=len(v)
v=v[:start]+'''        active_count = sum(line["status"] != "CANCELLED" for line in lines)
        return {"customer_order_id": order_id, "order_no": headers[0]["order_no"], "document_status": headers[0]["status"],
                "execution_status": order_progress_status(lines), "line_count": len(lines),
                "active_line_count": active_count, "cancelled_line_count": len(lines) - active_count,
                "lines": lines}
''';files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.js";v=read(p)
v=v.replace('REQUIRES_UOM:"Проверьте единицы товара"','REQUIRES_UOM:"Проверьте единицы товара",OVER_PICKED:"Превышение отбора — требуется разбор",SHORT_CLOSED:"Отбор закрыт с недостачей",PARTIAL_REFUSED:"Есть недостача; другие строки ещё в работе",CANCELLED:"Все строки отменены; физический факт показан отдельно",RESERVED:"Запас закреплён; физический отбор не подтверждён"',1)
v=v.replace('+" · склад "+result.warehouse_id;','+" · склад "+result.warehouse_id+" · активных строк "+result.active_line_count+", отменено "+result.cancelled_line_count;',1)
needle='      for(const value of[line.line_no,line.articul,line.requested_quantity,line.picked_quantity,line.remaining_quantity,line.base_uom||line.unit_code,line.reason]){'
assert needle in v
v=v.replace(needle,'''      tr.dataset.executionStatus=line.status;
      const base=line.base_uom||"базовая ед. не определена";
      const quantity=(value,unit)=>value==null?"—":String(value)+" "+unit;
      const state={PICKED:"Подтверждено",OVER_PICKED:"Превышение",CANCELLED:"Отменено",REFUSED:"Недостача",PARTIAL_REFUSED:"Частично / недостача",RESERVED:"Резерв",WAIT_STOCK:"Нет запаса",PARTIAL:"Частично",REQUIRES_UOM:"Единицы не согласованы"}[line.status]||line.status;
      for(const value of[line.line_no,line.articul,quantity(line.requested_quantity,line.requested_uom||line.base_uom||line.unit_code),
        quantity(line.picked_quantity,base),quantity(line.hard_quantity,base),
        line.status==="CANCELLED"?"— (отменено)":quantity(line.remaining_quantity,base),state,line.reason]){''',1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";v=read(p).replace('<th>Подтверждено</th><th>Осталось</th><th>Ед.</th><th>Причина</th>','<th>Подтверждено</th><th>Действующий резерв</th><th>Осталось</th><th>Состояние</th><th>Причина</th>',1).replace('order-execution.js?v=20261013-922','order-execution.js?v=20261013-1015');files[p]=v
print(json.dumps(files,ensure_ascii=True))
