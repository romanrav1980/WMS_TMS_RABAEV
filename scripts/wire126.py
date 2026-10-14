from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .stock_posting_uow import StockPosting","from .stock_posting_uow import StockPosting\nfrom ...platform.public import read_oracle_json\nfrom typing import Any",1)
s=s.replace("def _post(command):","def _post(command: StockCommand) -> dict[str,Any]:")
s=s.replace("def apply_mes_movements(gateway, production_order_id: int, request, actor: str | None):","def apply_mes_movements(gateway: Any, production_order_id: int, request: Any, actor: str | None) -> dict[str,Any]|None:")
s=s.replace('original = json.loads(value.read() if hasattr(value, "read") else value)','original = read_oracle_json(value)')
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.html");s=p.read_text(encoding="utf-8")
s=s.replace('<h2>Регистрация найденной маркированной паллеты</h2>','<h2>Подтверждение маркированного товара</h2><label>Источник товара<select id="tmBirthKind"><option value="INVENTORY">Паллета найдена при пересчёте</option><option value="MES">Паллета выпущена производством</option></select></label><label>Производственный заказ<input id="tmProductionOrder" inputmode="numeric"></label><label>Движение выпуска MES<input id="tmMovement" inputmode="numeric"></label>')
s=s.replace('data-permission="stock_inventory_count"><h2>Подтверждение','><h2>Подтверждение')
s=s.replace('Состав отправителя должен относиться к этой ревизии, паллете и товару.','Состав отправителя должен относиться к выбранному источнику, складу, паллете и товару. Для MES укажите существующее движение выпуска; повтор не создаёт новый товар.')
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/trace-manifests.js");s=p.read_text(encoding="utf-8").replace('main input,main textarea,main button','main input,main select,main textarea,main button')
s=s.replace('["tmManifest","tmRevision"','["tmProductionOrder","tmMovement","tmManifest","tmRevision"')
start=s.index(' el("tmBirth").addEventListener(');end=s.index(' el("tmLoad").addEventListener(',start)
s=s[:start]+""" el("tmBirth").addEventListener("click",()=>{if(busy||pending)return;try{const isMes=el("tmBirthKind").value==="MES";if(!auth().hasPermission(isMes?"mes_wms_bridge_apply":"stock_inventory_count"))throw Error("Нет права подтверждать выбранный источник товара.");const revision=Number(el("tmRevision").value);if(!isMes&&(!Number.isSafeInteger(revision)||revision<1))throw Error("Укажите действующую ревизию.");const aggregations=JSON.parse(el("tmScans").value);if(!Array.isArray(aggregations)||!aggregations.length)throw Error("Укажите сканы обязательных агрегаций.");const capture={manifest_operation_id:el("tmManifest").value,units:[],aggregations},uid=el("tmPallet").value;let body,path;if(isMes){const order=Number(el("tmProductionOrder").value),movement=Number(el("tmMovement").value);if(!Number.isSafeInteger(order)||order<1||!Number.isSafeInteger(movement)||movement<1||!uid)throw Error("Укажите производственный заказ, движение выпуска и паллету.");body={operation_id:"TRACE.MES:"+crypto.randomUUID(),movement_ids:[movement],units_by_movement:{},birth_captures:{[uid]:capture}};path="/api/mes/production-orders/"+order+"/apply-wms";}else{body={operation_id:"TRACE.BIRTH:"+crypto.randomUUID(),revision_id:revision,uid,cell:el("tmCell").value,article:el("tmArticle").value,quantity:el("tmQty").value,expiry_date:el("tmExpiry").value,price:el("tmPrice").value,reason:el("tmReason").value,capture};path="/api/inventory/stock-posting/inventory/lots";}pending={path,body,confirmed:false};localStorage.setItem(key(),JSON.stringify(pending));send();}catch(e){pending=null;say(e.message);controls();}});
"""+s[end:]
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
