from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/st-waiting-tasks.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("  loading=true;controls();\n  try{\n   const result=await request", "  if(!after){shownDecision=null;places=[];selectionRequired=false;renderPlaces();}\n  loading=true;controls();\n  try{\n   const result=await request",1)
html="wiki-raw/wms_admin_ui_reference/day-reconciliation.html"
print(json.dumps({p:s,html:Path(html).read_text(encoding="utf-8").replace("st-waiting-tasks.js?v=20261013-1084","st-waiting-tasks.js?v=20261013-1088")},ensure_ascii=True))
