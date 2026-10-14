from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
needle='        return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source={"plan_operation_id":plan_id},lines=(),metadata=metadata))'
if needle in s:
 s=s.replace("from ..contracts_stock import StockCommand","from ..contracts_stock import StockCommand,StockPostingError")
 s=s.replace(needle,'''        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source={"plan_operation_id":plan_id},lines=(),metadata=metadata))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc''')
s=s.replace('DECISION_REFERENCE,p.ACTOR,','DECISION_REFERENCE,p.ACTOR,json_value(p.SOURCE_COMPOSITION_JSON,\'$.nodes[0].article\') ARTICLE,json_value(p.SOURCE_COMPOSITION_JSON,\'$.nodes[0].quantity\') QUANTITY,json_value(p.SOURCE_COMPOSITION_JSON,\'$.nodes[0].base_uom\') BASE_UOM,(select t.TRANSPORT from RRL_TRANSPORT_TASK t where t.ID=p.SOURCE_TT_ID) VEHICLE_NUMBER,')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
if 'id="iwPhysicalPlan"' not in s:s=s.replace('<button id="iwRetry"',"""<section class="panel" data-permission="interwarehouse_receive"><h2>Физическая выгрузка и приёмка</h2><label>План<select id="iwPhysicalPlan"></select></label><label>Идентификатор паллеты, скан<input id="iwPallet" maxlength="200"></label><label>Автомобиль первого плеча, скан<input id="iwVehicle" maxlength="60"></label><label>Ворота принимающего склада, скан<input id="iwUnloadDock" maxlength="60"></label><button id="iwUnload">Подтвердить выгрузку</button><label>Приёмочная ячейка, скан<input id="iwCell" maxlength="60"></label><label>ШК артикула, скан<input id="iwBarcode" maxlength="128"></label><label>Артикул<input id="iwArticle" maxlength="160"></label><label>Фактическое количество в базовой единице<input id="iwQty" inputmode="decimal"></label><label>Базовая единица<input id="iwUom" maxlength="20"></label><button id="iwReceive">Принять весь исходный состав</button><p>Выгрузка подтверждает передачу груза. Приёмка создаёт остаток в заблокированной приёмочной ячейке; затем требуется размещение. Расхождение, вложенный или маркированный груз требуют соответствующего процесса.</p></section><button id="iwRetry" """,1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('el("iwRows").replaceChildren(...rows.map','el("iwPhysicalPlan").replaceChildren(...rows.filter(r=>!r.receipt_operation_id).map(r=>new Option(r.pallet_identifier+" · "+r.quantity+" "+r.base_uom+" · "+(r.unload_operation_id?"выгружено":"ожидает выгрузки"),r.operation_id)));el("iwRows").replaceChildren(...rows.map')
s=s.replace('+" · план "+r.operation_id','+" · план "+r.operation_id+" · "+(r.receipt_operation_id?"Принято, требуется размещение":r.unload_operation_id?"Выгружено, требуется приёмка":"Ожидает выгрузки")')
s=s.replace('await request("/plan",intent.body)','await request(intent.path||"/plan",intent.body)')
s=s.replace('say("План сохранён. Перейдите к физической выгрузке и приёмке.");','say(intent.path==="/receive"?"Товар принят в приёмочную ячейку. Требуется размещение.":intent.path==="/unload"?"Выгрузка подтверждена. Требуется приёмка.":"План сохранён. Перейдите к физической выгрузке и приёмке.");el("iwPhysicalPlan").replaceChildren();')
s=s.replace('el("iwRows").replaceChildren();document.querySelectorAll','el("iwRows").replaceChildren();el("iwPhysicalPlan").replaceChildren();document.querySelectorAll')
needle=' el("iwLoad").addEventListener'
if 'async function physical(' not in s:
 s=s.replace(needle,''' async function physical(path){if(busy||pending)return;try{const body={operation_id:"INTERWARE.PHYSICAL:"+crypto.randomUUID(),plan_operation_id:el("iwPhysicalPlan").value,scan_pallet:el("iwPallet").value.trim()};if(path==="/unload")Object.assign(body,{scan_vehicle:el("iwVehicle").value.trim(),scan_dock:el("iwUnloadDock").value.trim()});else Object.assign(body,{scan_cell:el("iwCell").value.trim(),scan_article:el("iwBarcode").value.trim(),article:el("iwArticle").value.trim(),quantity:el("iwQty").value.trim(),base_uom:el("iwUom").value.trim()});if(Object.values(body).some(v=>!v))throw Error("Выберите план и заполните сканы и количество.");const intent={path,body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());}catch(e){say(e.message);}}
 el("iwUnload").addEventListener("click",()=>physical("/unload"));el("iwReceive").addEventListener("click",()=>physical("/receive"));
'''+needle)
s=s.replace('++serial;el("iwRows").replaceChildren();','++serial;el("iwRows").replaceChildren();el("iwPhysicalPlan").replaceChildren();')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
