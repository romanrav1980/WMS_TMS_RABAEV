from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/st-waiting-tasks.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("busy||loading||!!p||!selected||(selectionRequired","busy||loading||!!p||!selected||selected!==shownDecision||(selectionRequired",1)
s=s.replace("window.addEventListener('wms-admin-auth-ready',()=>{el('swDecision').value='';el('swMessage').textContent='';resetRows();controls();});","""function openLinkedDecision(){
  const decision=new URLSearchParams(window.location.search).get('decision_operation_id');
  if(auth().state.user?.username&&decision&&/^[A-Za-z0-9_.:-]{1,100}$/.test(decision)){
   el('swDecision').value=decision;controls();read();
  }
 }
 window.addEventListener('wms-admin-auth-ready',()=>{el('swDecision').value='';el('swMessage').textContent='';resetRows();controls();openLinkedDecision();});""")
s=s.replace(" controls();\n})();"," controls();openLinkedDecision();\n})();")
html="wiki-raw/wms_admin_ui_reference/day-reconciliation.html"
print(json.dumps({p:s,html:Path(html).read_text(encoding="utf-8").replace("st-waiting-tasks.js?v=1078","st-waiting-tasks.js?v=1084")},ensure_ascii=True))
