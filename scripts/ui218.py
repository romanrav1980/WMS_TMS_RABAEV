from pathlib import Path
import json
out={};d=Path("wiki-raw/wms_admin_ui_reference")
p=d/"transport-loading.html";s=p.read_text(encoding="utf-8");anchor='<p id="unloadStatus" role="status"></p>';assert anchor in s;s=s.replace(anchor,anchor+'<div id="unloadQualityLinks" aria-label="Контроль выгруженных СТ"></div>',1);out[str(p)]=s
p=d/"transport-unloading.js";s=p.read_text(encoding="utf-8")
s=s.replace("slotGeneration = 0;","slotGeneration = 0, restoredShipments = [], currentMembers = [];",1)
s=s.replace("  tripId = data.trip.id;","  tripId = data.trip.id;currentMembers = data.members;showQualityLinks();",1)
anchor=" function resetSlots() {"
helper=""" function showQualityLinks() {
  const target = el("unloadQualityLinks");target.replaceChildren();
  if (!window.wmsAdminAuth.hasPermission("outgoing_pallet_check")) return;
  for (const id of restoredShipments) {
   const shipment = currentMembers.find(item => item.id === id);
   if (!shipment?.pallet_uid) continue;
   const link = document.createElement("a");
   link.href = "warehouse-tasks.html?qc_shipment=" + encodeURIComponent(shipment.pallet_uid);
   link.textContent = "Повторный контроль СТ " + (shipment.st_number || shipment.pallet_uid);
   target.append(link, document.createElement("br"));
  }
 }
"""
assert anchor in s;s=s.replace(anchor,helper+anchor,1)
s=s.replace('   pending = null;status("Выгрузка подтверждена:', '   restoredShipments = (result.members || []).map(item => item.shipment_id);\n   pending = null;status("Выгрузка подтверждена:',1)
s=s.replace('  rows = [];tripId = null;pending = null;','  rows = [];tripId = null;pending = null;restoredShipments = [];currentMembers = [];showQualityLinks();',1)
# Save durable command BEFORE making it eligible for retry, including quota errors.
s=s.replace('const key = scope();pending = {body, trip_id: tripId};localStorage.setItem(key, JSON.stringify(pending));await send(key);','const key = scope(), saved = {body, trip_id: tripId};localStorage.setItem(key, JSON.stringify(saved));pending = saved;await send(key);',1)
out[str(p)]=s
p=d/"outgoing-quality.js";s=p.read_text(encoding="utf-8");anchor='else if(draft){el("id").value=draft.identifier;message.textContent="Сканы сохранены. Предъявите текущий состав.";}';assert anchor in s;s=s.replace(anchor,anchor+'''
    else {
     const requested=new URLSearchParams(window.location.search).get("qc_shipment");
     if(requested && requested.length<=150){el("id").value=requested;message.textContent="Выгруженная СТ: предъявите актуальный состав к повторному контролю.";}
    }''',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
