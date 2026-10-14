from pathlib import Path
import json
f={};p="wiki-raw/wms_admin_ui_reference/warehouse-task-layout.js";s=Path(p).read_text(encoding="utf-8")
needle="tools.append(summary,content);for(const panel of panels)content.appendChild(panel);main.appendChild(tools);"
assert needle in s
s=s.replace(needle,needle+"""
 function focusLinkedPanel(){
  const id=window.location.hash.slice(1)||(new URLSearchParams(window.location.search).has('qc_shipment')?'outgoingQuality':'');
  const target=id?document.getElementById(id):null;
  if(target&&content.contains(target)){tools.open=true;target.scrollIntoView({block:'start'});}
 }
 window.addEventListener('wms-admin-auth-ready',()=>requestAnimationFrame(focusLinkedPanel));
 focusLinkedPanel();
""",1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";f[p]=Path(p).read_text(encoding="utf-8").replace("warehouse-task-layout.js?v=20261013-811","warehouse-task-layout.js?v=20261013-1095")
p="wiki/components/retailcase_ni051_control_label_20261012.md";f[p]=Path(p).read_text(encoding="utf-8")+"\n1095: actual browser found linkedQC hidden inside old collapsed additionaloperations. Existing layout now opens only explicitly linked containedpanel and focuses after auth-ready. Screenshot35 initially showedqueue, notQC; preserve it as unsuccessful navigation evidence. Fresh visibleQC capture pending.\n"
f["wiki/index.md"]="- [QC navigation1095](components/retailcase_ni051_control_label_20261012.md): explicit linked panel opens existing folded tools after auth; screenshot35 is queue, not QC proof.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1095: real browser exposed collapsed-layout QC link issue; focused existing panel opening on explicit hash/query, no command sent, screenshot35 not claimedQC.\n"
print(json.dumps(f,ensure_ascii=True))
