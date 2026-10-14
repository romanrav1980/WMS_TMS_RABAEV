from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.js");s=p.read_text(encoding="utf-8-sig")
s=s.replace('offers=[],pending=null','offers=[],bookings=[],pending=null',1)
s=s.replace(' async function balances()', ''' function clearBookings(){bookings=[];el("tareBooked").replaceChildren();}
 async function loadBookings(){await read(async current=>{const ware=number("tareWare"),trip=number("tareTrip"),type=number("tareType"),data=await request("/warehouses/"+ware+"/trips/"+trip+"/loaded-bookings");if(!current())return;bookings=data.filter(row=>row.pallet_type_id===type);el("tareBooked").replaceChildren(...bookings.map(row=>{const label=document.createElement("label"),input=document.createElement("input");input.type="checkbox";input.value=row.operation_id;label.append(input,document.createTextNode(row.place_kind+" "+row.place_id+" · "+row.pallet_type_name));return label;}));say(bookings.length?"Выберите тару погруженных мест, передаваемую водителю.":"Для этого типа нет закреплённой тары фактически погруженных мест.");});}
 async function balances()''',1)
s=s.replace('return{task_id:trip,owner_ware_id:number("tareWare")','const ids=Array.from(el("tareBooked").querySelectorAll("input:checked"),n=>n.value);if(ids.some(id=>!bookings.some(row=>row.operation_id===id&&row.tt_id===trip&&row.pallet_type_id===number("tareType"))))throw Error("Обновите список погруженных мест.");if(ids.length&&el("tareCondition").value!=="GOOD")throw Error("Закреплённая тара передаётся как пригодная.");if(BigInt(quantity("tareOfferQty"))<BigInt(ids.length))throw Error("Количество меньше выбранных физических мест.");return{...(ids.length?{booking_operation_ids:ids}:{}),task_id:trip,owner_ware_id:number("tareWare")',1)
s=s.replace('function resetData(){++serial;','function resetData(){clearBookings();++serial;',1)
s=s.replace('[["tareDebt",debt]','[["tareLoadBookings",loadBookings],["tareDebt",debt]',1)
s=s.replace('()=>{rows=null;offers=[];','()=>{clearBookings();rows=null;offers=[];',1)
s=s.replace(' el("tareRetry").addEventListener',' el("tareType").addEventListener("change",clearBookings);\n el("tareRetry").addEventListener',1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.html");s=p.read_text(encoding="utf-8-sig").replace('<h2>Выдача водителю</h2>','<h2>Выдача водителю</h2><button id="tareLoadBookings">Показать закреплённую тару погруженных мест</button><div id="tareBooked"></div><p>Один выбранный верхний паллет или контейнер — одна единица тары. Вложенный товар повторно не учитывается.</p>',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_routes.py");s=p.read_text(encoding="utf-8-sig").replace("from typing import Any,Literal","from typing import Annotated,Any,Literal").replace("booking_operation_ids: list[str]","booking_operation_ids: list[Annotated[str,Field(strict=True,min_length=1,max_length=100,pattern=r\"^[A-Za-z0-9_.:-]+$\")]]")
out[str(p)]=s
p=Path("scripts/build102_author_case.py");s=p.read_text(encoding="utf-8-sig").replace('# The existing final cleanup touches only its own goods P/H through the same core.','begin=s.index(\'  state=loading.status(trip);\');end=s.index(\'  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu\',begin)\ns=s[:begin]+s[end:]\n# The existing final cleanup touches only its own goods P/H through the same core.');out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-10_ni063_tare_assembly/004_tare_command.sql","../2026-10-10_ni063_booked_handover/003_tare_command.sql") for x in m["components"]]
for group,names in {"components":["002_helper.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["004_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_booked_handover/"+name
  if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
