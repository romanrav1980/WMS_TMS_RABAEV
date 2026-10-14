from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/day-inspection.js");s=p.read_text(encoding="utf-8")
s=s.replace('const identity=scope();let command=pending;', 'const identity=scope();let command=pending;')
s=s.replace('busy=true;controls();const result=await api(', 'if(localStorage.getItem(key())!==JSON.stringify(command))throw Error("Сохранённая команда изменена другой вкладкой. Перезагрузите форму и проверьте исход.");\n   busy=true;controls();const result=await api(')
s=s.replace('localStorage.removeItem(key());pending=null;context=null;', 'if(localStorage.getItem(key())!==JSON.stringify(command))throw Error("Сохранённая команда изменена во время запроса. Исход подтверждён сервером; перечитайте форму.");\n   localStorage.removeItem(key());pending=null;context=null;')
s=s.replace('window.addEventListener("wms-admin-auth-ready",changed);changed();', 'window.addEventListener("storage",event=>{if(event.key===key()){changed();message("Сохранённая команда изменена другой вкладкой. Проверьте её исход.");}});\n window.addEventListener("wms-admin-auth-ready",changed);changed();')
import json
print(json.dumps({str(p):s},ensure_ascii=True))
