from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");s=p.read_text(encoding="utf-8").replace('import { useEffect','import {parseReceiptIntent} from "./receiptIntentValidation";\nimport { useEffect')
s=s.replace('const inFlight=useRef(false);','const inFlight=useRef(false),loadedScope=useRef(""),corruptRef=useRef(false);\n const [corrupt,setCorrupt]=useState(false);')
s=s.replace('  setPlaces([]);setPreview(null);setMessage("");','  loadedScope.current=key;setPlaces([]);setPreview(null);setPending(null);setMessage("");')
s=s.replace('try {setPending(JSON.parse(localStorage.getItem(key)||"null") as PendingReceipt|null);}','try {setPending(parseReceiptIntent(localStorage.getItem(key),address));corruptRef.current=false;setCorrupt(false);}')
s=s.replace('catch {setPending(null);setMessage("Не удалось прочитать сохранённую операцию.");}','catch {corruptRef.current=true;setCorrupt(true);setMessage("Сохранённая операция повреждена. Новая отправка заблокирована; сохраните архив и перечитайте места.");}')
s=s.replace('async function loadPlaces() {','async function loadPlaces(recover=false) {').replace('  if(busy)return;\n  const scope=key;setBusy(true);','  if(busy||inFlight.current||loadedScope.current!==key||(corruptRef.current&&!recover))return;\n  const scope=key,damaged=recover?localStorage.getItem(key):null;setBusy(true);',1)
s=s.replace('   const data=await receiptRequest<StorePlace[]>','   if(recover){if(!corruptRef.current)throw Error("Черновик уже изменён.");localStorage.setItem("store-receipt-archive:"+scope+":"+crypto.randomUUID(),damaged||"");}\n   const data=await receiptRequest<StorePlace[]>',1)
s=s.replace('if(current.current===scope){setPlaces(data);','if(current.current===scope){if(recover){if(localStorage.getItem(scope)!==damaged)throw Error("Черновик изменён другой вкладкой.");localStorage.removeItem(scope);corruptRef.current=false;setCorrupt(false);setPending(null);}\n    setPlaces(data);',1)
s=s.replace('  if(busy)return;\n  const scope=key;setBusy(true);setPreview(null);','  if(busy||inFlight.current||loadedScope.current!==key||corruptRef.current)return;\n  const scope=key;setBusy(true);setPreview(null);')
s=s.replace('if(busy||inFlight.current)return;inFlight.current=true;setBusy(true);','if(busy||inFlight.current||loadedScope.current!==scope||current.current!==scope||corruptRef.current)return;const savedRaw=localStorage.getItem(scope);if(!savedRaw||JSON.stringify(parseReceiptIntent(savedRaw,address)?.body)!==JSON.stringify(intent.body)){setMessage("Сохранённая команда изменилась. Перезагрузите форму.");return;}inFlight.current=true;setBusy(true);')
s=s.replace('   localStorage.removeItem(scope);','   if(localStorage.getItem(scope)!==savedRaw)throw Error("Черновик изменился во время запроса. Сервер ответил; перечитайте места.");\n   localStorage.removeItem(scope);')
s=s.replace('if(current.current===scope){\n    const saved=', 'if(current.current===scope&&localStorage.getItem(scope)===savedRaw){\n    const saved=')
s=s.replace('if(busy||inFlight.current||pending||!preview)return;','if(busy||inFlight.current||pending||!preview||loadedScope.current!==key||corruptRef.current)return;')
s=s.replace('if(!busy&&pending?.confirmedRejection){','if(!busy&&!inFlight.current&&loadedScope.current===key&&pending?.confirmedRejection&&JSON.stringify(parseReceiptIntent(localStorage.getItem(key),address))===JSON.stringify(pending)){')
s=s.replace('return {places,preview,pending,busy,message,loadPlaces,show,confirm,','return {places,preview,pending,busy,message,corrupt,recover:()=>loadPlaces(true),loadPlaces,show,confirm,')
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreReceiptPanel.tsx");s=p.read_text(encoding="utf-8").replace('<fieldset disabled={flow.busy}>','<fieldset disabled={flow.busy}>\n   {flow.corrupt&&<button onClick={()=>void flow.recover()}>Сохранить повреждённую операцию в архив и перечитать места</button>}')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
