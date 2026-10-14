from pathlib import Path
import json
out={};p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.html");s=p.read_text(encoding="utf-8");out["db/migrations/2026-10-11_ni062_marked_receiving/000_before_store-return-receiving.html"]=s
s=s.replace('<label>Фактическое количество','<fieldset id="receiveUnitScans" hidden><legend>Уникальные коды возврата</legend></fieldset>\n<label>Фактическое количество',1).replace('<script src="store-return-receiving.js">','<script src="unit-scan-draft.js"></script><script src="store-return-receiving.js">');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-receiving.js");s=p.read_text(encoding="utf-8").replace(" let rows=[]"," const markDraft=window.wmsUnitScanDraft(document.getElementById('receiveUnitScans'));\n let rows=[]",1)
start=s.index(" function summary()");end=s.index("\n async function load()",start)
chunk=s[start:end];chunk=chunk.replace("function summary(){","function summary(){const source=selected();markDraft.setContext(source?.marked_unit_control||null,key()+':'+(source?.pickup_operation_id||''));",1);s=s[:start]+chunk+s[end:]
s=s.replace('  pending={body};const scope=key();', '  try{const scans=markDraft.getScans();if(scans.length)body.scans=scans;}catch(error){say(error.message);return;}\n  pending={body};const scope=key();',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
