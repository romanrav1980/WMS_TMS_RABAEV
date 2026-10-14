from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8")
old='''if(data.shipment_identifier!==id&&data.requested_identifier!==id)throw Error("Ответ относится к другой СТ.");
    if(typeof data.shipment_identifier!=="string"||!data.shipment_identifier)throw Error("Источник контроля не подтверждён.");
    el("id").value=data.shipment_identifier;'''
s=s.replace(old,"adoptIdentifier(data,id);")
needle=" async function readOnly(){"
helper=''' function adoptIdentifier(data,requested){
  if(data.shipment_identifier!==requested&&data.requested_identifier!==requested)throw Error("Ответ относится к другой СТ.");
  if(typeof data.shipment_identifier!=="string"||!data.shipment_identifier||data.shipment_identifier.length>150)throw Error("Источник контроля не подтверждён.");
  el("id").value=data.shipment_identifier;
 }
'''
s=s.replace(needle,helper+needle)
s=s.replace('if(current===generation&&el("id").value.trim()===requested)show(data);','if(current===generation&&el("id").value.trim()===requested){adoptIdentifier(data,requested);show(data);}')
p2=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html");t=p2.read_text(encoding="utf-8").replace("outgoing-quality.js?v=20261013-1126","outgoing-quality.js?v=20261013-1129")
print(json.dumps({str(p):s,str(p2):t},ensure_ascii=True))
