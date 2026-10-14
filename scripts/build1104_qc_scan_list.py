from pathlib import Path
import json
f={};p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('<p data-count class="qc-count"></p>','<p data-count class="qc-count"></p><div data-scan-list class="qc-scan-list"></div>',1)
needle='  el("load").textContent=pending?"Повторить сохранённую команду":"Предъявить к контролю";'
assert needle in s
s=s.replace(needle,needle+"""
  const editable=!busy&&!broken&&!pending&&snapshot?.composition_signature===draft?.signature&&snapshot?.shipment_identifier===draft?.identifier;
  window.wmsQualityScanView.render(el("scan-list"),draft?.entries||[],Boolean(editable),removeScan);
""",1)
needle=' function append(entry){'
assert needle in s
s=s.replace(needle,""" function removeScan(index){
  if(!currentDraft()||!Number.isSafeInteger(index)||index<0||index>=draft.entries.length)return;
  const removed=draft.entries.splice(index,1)[0];
  try{saveDraft();}catch(error){draft.entries.splice(index,0,removed);message.textContent=error.message;controls();}
 }
"""+needle,1)
s=s.replace('function count(){el("count").textContent=','function count(){el("count").textContent=',1)
# Existing saveDraft and controls refresh the bounded list; all direct draft clear paths refresh too.
s=s.replace('draftRaw=null;draft=snapshot?{identifier:snapshot.shipment_identifier,signature:snapshot.composition_signature,entries:[]}:null;count();',
'draftRaw=null;draft=snapshot?{identifier:snapshot.shipment_identifier,signature:snapshot.composition_signature,entries:[]}:null;count();controls();',1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.css";f[p]=Path(p).read_text(encoding="utf-8")+"""
.qc-scan-list{margin:14px 0}.qc-scan-heading{font-size:12px;color:#6b809a}.qc-scan-scroll{max-height:240px;overflow:auto;border:1px solid #e1e8f3;border-radius:8px}.qc-scan-scroll table{width:100%;border-collapse:collapse;font-size:12px}.qc-scan-scroll th{position:sticky;top:0;background:#f0f5fc;color:#607997;text-align:left}.qc-scan-scroll th,.qc-scan-scroll td{padding:10px;border-bottom:1px solid #e8edf6;vertical-align:top}.qc-scan-code{display:block;overflow-wrap:anywhere;color:#294e78}.qc-scan-scroll small{display:block;color:#7388a1;margin-top:4px}.qc-scan-scroll td:last-child{width:75px}.qc-scan-scroll button{padding:5px 8px;font-size:11px}
"""
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";s=Path(p).read_text(encoding="utf-8")
s=s.replace('<script src="outgoing-quality.js?v=20261013-1103"></script>','<script src="outgoing-quality-scan-view.js?v=20261013-1104"></script><script src="outgoing-quality.js?v=20261013-1104"></script>').replace('outgoing-quality.css?v=20261013-1096','outgoing-quality.css?v=20261013-1104')
f[p]=s
p="wiki/components/nicora_ni051_control_label_20261012.md";f[p]=Path(p).read_text(encoding="utf-8")+"\n1104: separate bounded draft scan renderer (last50, counts notphysicalunits); barcode/profile and per-scan removal before confirmedcommand, same currentdraft/raw/scope guards. Pendingoriginalbody cannotbeedited; nativefullcoverage remainsauthoritative. Actual emptyunmarkedCASE screenshot next, no fabricatedscans.\n"
f["wiki/index.md"]="- [QC scan draft1104](components/nicora_ni051_control_label_20261012.md): bounded separate renderer/profile-aware evidence and per-scan correction before confirmation.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1104: continue QC functional workflow, separate last50 scan view and scoped pre-submit correction; no physicalcount inferred from multipleprofiles, no nativewriter change.\n"
print(json.dumps(f,ensure_ascii=True))
