import json
from pathlib import Path
out={}
def patch(p,a,b):
 v=out.get(p,Path(p).read_text(encoding="utf-8"));assert v.count(a)==1,(p,a,v.count(a));out[p]=v.replace(a,b)
p="wiki-raw/wms_admin_ui_reference/tare-resolutions.html"
patch(p,'<p id="trCaseSource"></p>', '<p id="trCaseSource"></p><label title="Списать количество, которое по подтверждённым передачам вернулось на склад-владелец"><input id="trWarehouseReturn" type="checkbox">Списание после возврата на склад</label><p id="trCustodySource"></p>')
p="wiki-raw/wms_admin_ui_reference/tare-resolutions.js"
patch(p,"let context=null,loans=[],cases=[],pending=null","let context=null,loans=[],cases=[],custody=[],custodyMore=false,pending=null")
patch(p,'function clearSources(){loans=[];cases=[];', 'function clearSources(){loans=[];cases=[];custody=[];custodyMore=false;el("trWarehouseReturn").checked=false;el("trCustodySource").textContent="";')
patch(p,'const data=await request("/warehouses/"+number("trWare")+"/damage-cases");if(!current())return;cases=data;',
 'const ware=number("trWare"),[data,positions]=await Promise.all([request("/warehouses/"+ware+"/damage-cases"),request("/warehouses/"+ware+"/damage-custody")]);if(!current())return;cases=data;custody=positions.items;custodyMore=positions.has_more;')
patch(p,'function summary(){const r=', 'function summary(){const selected=el("trCase").value,positions=custody.filter(r=>r.damage_operation_id===selected);el("trCustodySource").textContent=positions.length?positions.map(r=>r.custodian_kind+" "+r.custodian_id+" · повреждение "+r.damage_operation_id+" · доступное связанное количество "+r.tracked_quantity).join("; "):"Подтверждённого текущего количества с этим источником повреждения в доступных местах нет.";if(custodyMore)el("trCustodySource").textContent+=" Показаны первые200 позиций; отсутствие позиции не подтверждает отсутствие тары.";const r=')
patch(p,'return{damage_operation_id:row.operation_id,quantity:quantity("trLossQty"),reason:el("trLossReason").value,decision_reference:el("trLossRef").value};',
 'const qty=quantity("trLossQty"),ware=number("trWare");if(el("trWarehouseReturn").checked){const position=custody.find(r=>r.damage_operation_id===row.operation_id&&r.custodian_kind==="WAREHOUSE"&&r.custodian_id===String(ware));if(!position||BigInt(qty)>BigInt(position.tracked_quantity))throw Error("Обновите акты: это количество с данным источником не подтверждено на складе.");}return{damage_operation_id:row.operation_id,...(el("trWarehouseReturn").checked?{writeoff_warehouse_id:ware}:{}),quantity:qty,reason:el("trLossReason").value,decision_reference:el("trLossRef").value};')
p="wiki-raw/wms_admin_ui_reference/tare-ledger.html"
patch(p,'<input id="tareOfferQty"', '<input id="tareOfferQty"')
# Insert an optional origin for warehouse outbound; existing GOOD payload stays unchanged.
patch(p,'<label>Скан машины<input id="tareOfferScan"', '<label title="Для отслеживаемой повреждённой тары укажите исходную операцию повреждения">Источник повреждения<input id="tareDamageOrigin" maxlength="100" autocomplete="off"></label><label>Скан машины<input id="tareOfferScan"')
p="wiki-raw/wms_admin_ui_reference/tare-ledger.js"
patch(p,'condition:el("tareCondition").value,from_kind:"WAREHOUSE"', 'condition:el("tareCondition").value,...(el("tareDamageOrigin").value.trim()?{damage_operation_id:el("tareDamageOrigin").value.trim()}:{}),from_kind:"WAREHOUSE"')
print(json.dumps(out))
