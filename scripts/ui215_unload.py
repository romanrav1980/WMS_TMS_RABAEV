from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni052_unload_slot")
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading.py")
out[str(f/"000_before_loading.py")]=p.read_text(encoding="utf-8")
out[str(p)]=p.read_text(encoding="utf-8").replace("DEPARTED_AT,CONTENT_VERSION,ROOT_CASE_TASK_ID,","DEPARTED_AT,CONTENT_VERSION,ROOT_CASE_TASK_ID,WARE_ID,")
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8")
anchor='<label>Машина<input id="unloadVehicle"'
idx=s.index(anchor)
extra='<button id="unloadLoadSlots" data-permission="warehouse_task_view" title="Показать места хранения в исходной ячейке.">Показать места хранения</button>\n<label>Место хранения<select id="unloadSlot" title="Выберите свободное место, если ячейка разделена на места хранения."><option value="">Без отдельного места</option></select></label>\n<label>Скан места хранения<input id="unloadSlotScan" autocomplete="off" title="Подтвердите адрес выбранного места хранения."></label>\n'
out[str(p)]=s[:idx]+extra+s[idx:]
p=Path("wiki-raw/wms_admin_ui_reference/transport-unloading.js");s=p.read_text(encoding="utf-8").replace("rows = [], tripId = null;","rows = [], tripId = null, slotGeneration = 0;")
s=s.replace('  el("unloadRetry").hidden','  el("unloadLoadSlots").disabled = busy || !!pending;\n  el("unloadRetry").hidden',1)
s=s.replace(' function showOrigin() {',' function resetSlots() {\n  slotGeneration++;\n  const option = document.createElement("option");option.value = "";option.textContent = "Без отдельного места";\n  el("unloadSlot").replaceChildren(option);el("unloadSlotScan").value = "";\n }\n function showOrigin() {\n  resetSlots();',1)
s=s.replace('   if (!body.scan_container','   if (el("unloadSlot").value) {\n    body.target_slot_id = Number(el("unloadSlot").value);body.scanned_to_slot_code = el("unloadSlotScan").value.trim();\n    if (!body.scanned_to_slot_code) throw new Error("Отсканируйте выбранное место хранения.");\n   } else if (el("unloadSlotScan").value.trim()) throw new Error("Выберите место хранения для этого скана.");\n   if (!body.scan_container',1)
anchor=' el("unloadSource").addEventListener'
idx=s.index(anchor)
extra=""" el("unloadLoadSlots").addEventListener("click", async () => {
  if (busy || pending || window.wmsPhysicalLoadState.isBusy() || window.wmsPhysicalLoadState.hasPending()) return;
  const row = rows.find(item => item.load_operation_id === el("unloadSource").value);
  if (!row) {status("Сначала обновите и выберите погруженное место.");return;}
  const key = scope(), generation = ++slotGeneration;
  try {
   const slots = await request("/api/warehouse-hus/target-slots?cell=" + encodeURIComponent(row.origin_cell) + "&warehouse=" + row.ware_id);
   if (key !== scope() || generation !== slotGeneration || row.load_operation_id !== el("unloadSource").value) return;
   resetSlots();
   for (const slot of slots) {
    const option = document.createElement("option");option.value = slot.cell_slot_id;
    option.textContent = slot.slot_code + (slot.unavailable_reason ? " · " + slot.unavailable_reason : "");
    option.disabled = !!slot.unavailable_reason;el("unloadSlot").appendChild(option);
   }
   status("Выберите и отсканируйте свободное место хранения. После выгрузки требуется контроль.");
  } catch (error) {if (key === scope() && generation === slotGeneration) status(error.message);}
 });
"""
out[str(p)]=s[:idx]+extra+s[idx:]
p=f/"checkpoint.json";j=json.loads(p.read_text(encoding="utf-8"));j["sha256"][str(f/"000_before_loading.py")]=hashlib.sha256(out[str(f/"000_before_loading.py")].encode()).hexdigest();out[str(p)]=json.dumps(j,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
