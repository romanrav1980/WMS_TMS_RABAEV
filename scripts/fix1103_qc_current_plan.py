from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('  el("id").disabled=busy||!!pending;el("read").disabled=busy;', '''  for(const name of ["scan","weight"])el(name).disabled=busy||broken||(!pending&&!snapshot?.composition_signature);
  for(const name of ["add-item","add-mark","last"])el(name).disabled=busy||broken||!!pending||!snapshot?.composition_signature;
  el("print-label").disabled=busy||broken||!snapshot?.shipment_identifier;
  el("id").disabled=busy||!!pending;el("read").disabled=busy;''',1)
old='   if(sent.kind==="plan"){show(result.control_status);}'
assert old in s
s=s.replace(old,'''   if(sent.kind==="plan"){
    snapshot=null;const current=++generation,data=await call(path(sent.identifier));
    if(current!==generation||el("id").value.trim()!==sent.identifier)return;
    if(data.shipment_identifier!==sent.identifier)throw Error("Актуальное чтение относится к другой СТ.");show(data);
   }''',1)
s=s.replace('if(gen===finalGeneration)message.textContent=error.message;','if(gen===finalGeneration&&!error.obsolete)message.textContent=error.message;',1)
p2="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html"
print(json.dumps({p:s,p2:Path(p2).read_text(encoding="utf-8").replace("outgoing-quality.js?v=20261013-1100","outgoing-quality.js?v=20261013-1103")},ensure_ascii=True))
