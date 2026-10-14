from pathlib import Path
import json
files={}
p="api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py"
t=Path(p).read_text(encoding="utf-8")
old="                       nvl(sum(r.ORDER_QTY), 0) TOTAL_ORDER_QTY,"
new="""                       nvl(sum(r.ORDER_QTY), 0) TOTAL_ORDER_QTY,
                       to_char(nvl(sum(r.ORDER_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') TOTAL_ORDER_QTY_EXACT,
                       count(distinct r.UNIT_CODE) ORDER_UOM_COUNT,
                       min(r.UNIT_CODE) ORDER_UOM,
                       count(case when r.UNIT_CODE is null then 1 end) UNKNOWN_UOM_ROWS,"""
assert old in t;t=t.replace(old,new);files[p]=t
p="wiki-raw/wms_admin_ui_reference/customer-orders.js"
t=Path(p).read_text(encoding="utf-8")
t=t.replace("escapeOrder(order.total_order_qty)",'escapeOrder(order.order_uom_count===1&&order.unknown_uom_rows===0 ? String(order.total_order_qty_exact??order.total_order_qty)+" "+order.order_uom : "См. позиции")')
t=t.replace("escapeOrder(row.order_qty)", "escapeOrder(row.order_qty_exact??row.order_qty)")
t=t.replace("escapeOrder(row.order_weight)", "escapeOrder(row.order_weight_exact??row.order_weight)")
t=t.replace("escapeOrder(row.pack_count)", "escapeOrder(row.pack_count_exact??row.pack_count)")
t=t.replace("sapLayoutRow(row.articul,String(row.order_qty))", "sapLayoutRow(row.articul,String(row.order_qty_exact??row.order_qty))")
files[p]=t
p="wiki-raw/wms_admin_ui_reference/customer-orders.html"
t=Path(p).read_text(encoding="utf-8")
import re
t=re.sub(r'customer-orders.js\?v=[^"]+', 'customer-orders.js?v=20261013-1042',t)
files[p]=t
print(json.dumps(files,ensure_ascii=True))
