from pathlib import Path
import ast,json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py";v=read(p)
arg=next(x for x in ast.walk(ast.parse(v))if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=="fetch_all").args[0]
sql=arg.value.replace("select f.*,ct.SSCC CASE_IDENTIFIER,ct.CURRENT_CELL CASE_CURRENT_CELL,ct.CONTENT_VERSION CASE_CURRENT_VERSION,ct.STATUS CASE_CURRENT_STATUS from (","select f.*,ct.SSCC CASE_IDENTIFIER,ct.CURRENT_CELL CASE_CURRENT_CELL,\n                   ct.CONTENT_VERSION CASE_CURRENT_VERSION,ct.STATUS CASE_CURRENT_STATUS\n              from (",1).replace(") f left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID and ct.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID and ct.WARE_ID=:p_warehouse order by f.FULFILLMENT_ID",") f left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID\n               and ct.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID and ct.WARE_ID=:p_warehouse\n             order by f.FULFILLMENT_ID",1)
v=v.replace(ast.get_source_segment(v,arg),'"""\n            '+sql+'\n            """',1).replace('        import json\n','',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/customer-orders.js";v=read(p)
needle='''      <td>${escapeOrder(row.pallet_uid || row.legacy_sborka_pallet_id)}</td>'''
assert v.count(needle)==1
v=v.replace(needle,'''      <td>${escapeOrder(row.pallet_uid || row.legacy_sborka_pallet_id)}
        ${row.case_place_current?'<br><a href="warehouse-hus.html?identifier='+encodeURIComponent(row.case_identifier)+'#huComposition">Текущий CASE '+escapeOrder(row.case_identifier)+' →</a><small class="order-case-location">Версия '+escapeOrder(row.case_current_version)+' · '+escapeOrder(row.case_current_cell)+'</small>':
          row.status==='PICKED'&&row.picked_case_task_id?'<small class="order-case-warning">Текущее размещение CASE не подтверждено</small>':''}</td>''',1)
v=v.replace('escapeOrder(row.fact_qty ?? "—")','escapeOrder(row.fact_qty_exact ?? row.fact_qty ?? "—")',1).replace('escapeOrder(row.fact_weight)','escapeOrder(row.fact_weight_exact ?? row.fact_weight)',1)
v=v.replace('escapeOrder(row.status)}${row.picked_at','escapeOrder(({PLANNED:"Подготовлена СТ",PICKED:"Отобрано",SHIPPED:"Отгружено",CANCELLED:"Отменено"})[row.status]||row.status)}${row.picked_at',1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";v=read(p).replace('<th>Паллет</th><th>Адрес</th><th>Факт</th>','<th>Место / СТ</th><th>Адрес</th><th>Факт</th>',1).replace('customer-orders.js?v=20261013-1022','customer-orders.js?v=20261013-1028').replace('order-execution.css?v=20261013-1023','order-execution.css?v=20261013-1028')
v=v.replace('<span>Факт комплектации / отгрузки</span>','<span>Подтверждённый отбор и отгрузка. Для текущего состава используйте ссылку на CASE.</span>',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.css";files[p]=read(p)+'\n.order-case-location{display:block;font-size:11px;color:#63758e;margin-top:5px}.order-case-warning{display:block;color:#aa6330;font-size:11px;margin-top:5px}\n'
print(json.dumps(files,ensure_ascii=True))
