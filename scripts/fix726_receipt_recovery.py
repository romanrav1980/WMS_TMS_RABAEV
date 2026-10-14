from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");s=p.read_text(encoding="utf-8")
old='const savedRaw=localStorage.getItem(scope);if(!savedRaw||JSON.stringify(parseReceiptIntent(savedRaw,address)?.body)!==JSON.stringify(intent.body)){setMessage("Сохранённая команда изменилась. Перезагрузите форму.");return;}'
new='let savedRaw:string|null=null;try{savedRaw=localStorage.getItem(scope);if(!savedRaw||JSON.stringify(parseReceiptIntent(savedRaw,address)?.body)!==JSON.stringify(intent.body))throw Error("Changed command");}catch{corruptRef.current=true;setCorrupt(true);setMessage("Сохранённая команда повреждена или изменена. Отправка заблокирована; перечитайте места.");return;}'
assert old in s;s=s.replace(old,new)
old='if(!busy&&!inFlight.current&&loadedScope.current===key&&pending?.confirmedRejection&&JSON.stringify(parseReceiptIntent(localStorage.getItem(key),address))===JSON.stringify(pending)){localStorage.removeItem(key);setPending(null);setPreview(null);setMessage("Исправьте данные и заново покажите состав.");}'
new='try{if(!busy&&!inFlight.current&&loadedScope.current===key&&pending?.confirmedRejection&&JSON.stringify(parseReceiptIntent(localStorage.getItem(key),address))===JSON.stringify(pending)){localStorage.removeItem(key);setPending(null);setPreview(null);setMessage("Исправьте данные и заново покажите состав.");}}catch{corruptRef.current=true;setCorrupt(true);setMessage("Сохранённая команда повреждена. Сохраните архив и перечитайте места.");}'
assert old in s;s=s.replace(old,new);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s=p.read_text(encoding="utf-8").replace('"outcome_confirmed":error.status<500','"outcome_confirmed":error.status<500 and error.status not in(401,403) and str(error)!="OPERATION_CONFLICT"');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
