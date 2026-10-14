from pathlib import Path
import json
d=Path("db/migrations/2026-10-13_ni072_waiting_tasks");out={}
p=d/"006_physical_body.sql";t=p.read_text(encoding="utf-8")
t=t.replace("items json_array_t:=json_array_t();","wait_cell varchar2(50);needs_move boolean:=false;items json_array_t:=json_array_t();")
anchor="  for x in(select f.FULFILLMENT_ID"
assert anchor in t
t=t.replace(anchor,"  select max(DEFER_WAIT_CELL)into wait_cell from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=p_ware;\n"+anchor)
anchor="   item:=json_object_t();item.put('fulfillment_id'"
assert anchor in t
t=t.replace(anchor,"   if wait_cell is null or x.TO_CELL!=wait_cell then needs_move:=true;end if;\n"+anchor)
t=t.replace("result.put('physical_move_required',true)","result.put('physical_move_required',needs_move)")
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");t=p.read_text(encoding="utf-8")
old="if(v.physical_preparation)el('sdMessage').textContent+=' Товар уже отобран: перенос рейса не перемещает его. Создайте штатное складское задание в зону ожидания.';"
new="if(v.physical_preparation)el('sdMessage').textContent+=v.physical_preparation.physical_move_required?' Товар уже отобран: перенос рейса не перемещает его. Создайте штатное складское задание в зону ожидания.':' Отобранный товар уже находится в настроенной ячейке ожидания; повторное перемещение не требуется.';"
assert old in t
out[str(p)]=t.replace(old,new)
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
out[str(p)]=t.replace("<th>Диспетчер</th></tr>","<th>Диспетчер</th><th>Ожидание</th></tr>")
print(json.dumps(out,ensure_ascii=True))
