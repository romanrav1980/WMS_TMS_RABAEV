from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/return_progress.py");s=p.read_text(encoding="utf-8").replace('from pathlib import Path','from ..contracts import StoreReceiptError\nfrom pathlib import Path').replace('    for raw in cursor.fetchall():','    for raw in cursor.fetchmany(101):').replace('        row["warehouse_progress_visible"]=True','        if row["approval_operation_id"]in result:\n            raise StoreReceiptError("RETURN_PROGRESS_AMBIGUOUS","Неоднозначная цепочка возврата; требуется сверка",409)\n        row["warehouse_progress_visible"]=True');files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-progress.js");s=p.read_text(encoding="utf-8").replace(' function stage(a,p){',' const driverUrl=new URL(location.href);driverUrl.port="3000";driverUrl.pathname="/";driverUrl.search="";driverUrl.hash="";\n function stage(a,p){').replace('"http://127.0.0.1:3000/"','driverUrl.href');files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/store-return-transport.js");s=p.read_text(encoding="utf-8")
old='say(rows.length?"":"Нет возвратов с основанием SAP, ожидающих планирования.");'
new='''const linked=new URLSearchParams(location.search).get("approval_id");if(linked&&rows.some(r=>r.approval_id===linked))el("transportApproval").value=linked;say(linked&&!rows.some(r=>r.approval_id===linked)?"Выбранного согласования нет в текущей очереди. Проверьте, не назначен ли уже вывоз.":rows.length?"":"Нет возвратов с основанием SAP, ожидающих планирования.");'''
assert old in s;s=s.replace(old,new)
s=s.replace('window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();','''window.addEventListener("wms-admin-auth-ready",changedAuth);changedAuth();
 let openedLink=false;
 function openLink(){if(openedLink||!auth().state.user||busy||pending||!new URLSearchParams(location.search).get("approval_id"))return;openedLink=true;void eligible();}
 window.addEventListener("wms-admin-auth-ready",openLink);openLink();''')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
