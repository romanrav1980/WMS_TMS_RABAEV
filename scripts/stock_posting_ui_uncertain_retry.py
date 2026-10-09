"""Never clear a durable operation after a previous unknown delivery outcome."""
import json
from pathlib import Path
d=Path("wiki-raw/wms_admin_ui_reference");out={}
for name in ("case-pick-posting.js","case-carrier-move.js","inventory-count.js"):
 p=d/name;s=p.read_text(encoding="utf-8");key="key" if name=="inventory-count.js" else "storageKey"
 declaration="    let "+key+";"
 assert s.count(declaration)==1
 s=s.replace(declaration,declaration+"\n    let attempted = false, priorUnknown = false;",1)
 needle='      const result = await api("/api/inventory/stock-posting/inventory/counts", body);' if key=="key" else ('      await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/move-carrier",' if name=="case-carrier-move.js" else '      await cpTsdFetch("/api/case-pick/tasks/"+intent.task+"/lines/"+intent.line+"/confirm",')
 assert s.count(needle)==1
 s=s.replace(needle,"      priorUnknown = !!localStorage.getItem("+key+' + ":delivery");\n'+"      localStorage.setItem("+key+' + ":delivery", "unknown"); attempted = true;\n'+needle,1)
 # The marker is written before HTTP: browser interruption remains an unknown attempt.
 needle="      localStorage.removeItem("+key+"); pending();" if key=="key" else "      localStorage.removeItem(storageKey);pending();"
 assert s.count(needle)>=1
 s=s.replace(needle,"      localStorage.removeItem("+key+' + ":delivery");\n'+needle,1)
 if name=="inventory-count.js":
  needle="      if (key && (error.detail?.outcome_confirmed === true)) {\n        localStorage.removeItem(key); pending();\n      }"
  replacement="""      if (attempted && !priorUnknown && error.detail?.outcome_confirmed === true) {
        localStorage.removeItem(key + ":delivery");
        localStorage.removeItem(key); pending();
      }"""
 else:
  needle="      if(storageKey&&(error.detail?.outcome_confirmed===true))localStorage.removeItem(storageKey);" if name=="case-carrier-move.js" else "      if(storageKey && (error.detail?.outcome_confirmed===true))localStorage.removeItem(storageKey);"
  replacement="""      if(attempted && !priorUnknown && error.detail?.outcome_confirmed===true) {
        localStorage.removeItem(storageKey + ":delivery");
        localStorage.removeItem(storageKey);
      }"""
 assert s.count(needle)==1
 s=s.replace(needle,replacement,1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
