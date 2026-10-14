import json
from pathlib import Path
files={}
path=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py")
text=path.read_text(encoding="utf-8")
text=text.replace("select f.*,ct.SSCC CASE_IDENTIFIER","select f.*,p.TRANSTASK_ID CURRENT_TRIP_ID,tt.CONDITION CURRENT_TRIP_CONDITION,tt.DOCK CURRENT_DOCK,ct.SSCC CASE_IDENTIFIER",1)
text=text.replace("order by f.FULFILLMENT_ID\n", "left join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID and p.WARE_ID=:p_warehouse\n               left join RRL_TRANSPORT_TASK tt on tt.ID=p.TRANSTASK_ID\n             order by f.FULFILLMENT_ID\n",1)
files[str(path)]=text
path=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js")
text=path.read_text(encoding="utf-8")
old='<td>'+chr(36)+'{escapeOrder(row.address_text)}</td>'
new='<td>'+chr(36)+'{escapeOrder(row.address_text)}'+chr(36)+'{Number.isSafeInteger(row.current_trip_id)&&row.current_trip_id>0?\'<br><a href="transport-loading.html?trip_id=\'+row.current_trip_id+\'" title="Открыть фактическую погрузку назначенного рейса.">Рейс №\'+escapeOrder(row.current_trip_id)+\' →</a><small class="order-case-location">\'+escapeOrder(row.current_trip_condition||"Статус не задан")+\' · ворота: \'+escapeOrder(row.current_dock||"не назначены")+\'</small>\':\'<small class="order-case-location">Рейс не назначен</small>\'}</td>'
assert old in text;text=text.replace(old,new,1)
files[str(path)]=text
path=Path("wiki-raw/wms_admin_ui_reference/transport-loading.js")
text=path.read_text(encoding="utf-8")
old='}controls();\n }\n window.wmsPhysicalLoadState='
new='}controls();\n  const initial=Number(new URLSearchParams(location.search).get("trip_id"));\n  if(!pending&&window.wmsAdminAuth.state.user?.username&&Number.isSafeInteger(initial)&&initial>0){el("tripId").value=String(initial);refresh();}\n }\n window.wmsPhysicalLoadState='
assert old in text;text=text.replace(old,new,1);files[str(path)]=text
path=Path("wiki-raw/wms_admin_ui_reference/partial-shipment-layout.js")
text=path.read_text(encoding="utf-8").replace("async function prepare() {","async function prepare() {\n    if(busy||window.cpTsdStockBusy||window.wmsCaseType?.hasPending())throw Error(\"Сначала завершите сохранённую складскую команду.\");",1);files[str(path)]=text
print(json.dumps(files,ensure_ascii=True))
