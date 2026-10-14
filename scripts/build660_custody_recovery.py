from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/useReturnCustody.ts");v=p.read_text(encoding="utf-8")
v=v.replace('import { custodyRequest }','import { parseCustodyIntent } from "./custodyIntentValidation";\nimport { custodyRequest }')
v=v.replace('const locked=useRef(false),pendingRef=useRef<CustodyIntent|null>(null);','const locked=useRef(false),pendingRef=useRef<CustodyIntent|null>(null),corruptRef=useRef<string|null>(null);')
v=v.replace('const [pending,setPending]=useState<CustodyIntent|null>(null),','const [corrupt,setCorrupt]=useState(false);\n const [pending,setPending]=useState<CustodyIntent|null>(null),')
a='try{const saved=JSON.parse(localStorage.getItem(key)||"null") as CustodyIntent|null;pendingRef.current=saved;setPending(saved);}'
b='try{const saved=parseCustodyIntent(localStorage.getItem(key));pendingRef.current=saved;setPending(saved);corruptRef.current=null;setCorrupt(false);}'
assert a in v;v=v.replace(a,b)
a='catch{pendingRef.current=null;setPending(null);setMessage("Не удалось прочитать сохранённую операцию.");}'
b='catch{pendingRef.current=null;setPending(null);corruptRef.current=key;setCorrupt(true);setMessage("Сохранённая операция повреждена. Отправка заблокирована; сохраните архив и перечитайте передачи.");}'
assert a in v;v=v.replace(a,b)
v=v.replace('async function load(){\n  if(locked.current||pendingRef.current)return;','async function load(recover=false){\n  if(locked.current||pendingRef.current||(corruptRef.current&&!recover))return;')
a='try{\n   if(mode==="store")'
b='''try{
   const damaged=recover?localStorage.getItem(scope):null;
   if(recover){if(corruptRef.current!==scope)throw Error("Сначала выберите повреждённый черновик.");localStorage.setItem("return-custody-archive:"+scope+":"+crypto.randomUUID(),damaged||"");}
   if(mode==="store")'''
assert a in v;v=v.replace(a,b)
a='if(current.current===scope)setMessage("");'
b='''if(current.current===scope){
    if(recover){if(localStorage.getItem(scope)!==damaged)throw Error("Черновик изменён другой вкладкой. Повторите восстановление.");localStorage.removeItem(scope);corruptRef.current=null;setCorrupt(false);}
    setMessage(recover?"Повреждённый черновик сохранён в архив. Перечитаны только ещё не подтверждённые передачи.":"");
   }'''
assert a in v;v=v.replace(a,b)
v=v.replace('if(locked.current||pendingRef.current)return;\n  if("quantity"', 'if(locked.current||pendingRef.current||corruptRef.current)return;\n  if("quantity"')
v=v.replace('return {storeRows,driverRows,pending,busy,message,load,confirm,restart,','return {storeRows,driverRows,pending,corrupt,busy,message,load:()=>load(),recoverCorrupt:()=>load(true),confirm,restart,')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/delivery/ReturnCustodyPanel.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('disabled={flow.busy||!!flow.pending}','disabled={flow.busy||!!flow.pending||flow.corrupt}')
a='  {flow.pending&&<button'
b='  {flow.corrupt&&<button disabled={flow.busy||!username||!password||(mode==="store"&&!address)} onClick={()=>void flow.recoverCorrupt()}>Сохранить повреждённый черновик и перечитать передачи</button>}\n'+a
assert a in v;v=v.replace(a,b)
v=v.replace('disabled={!!flow.pending||!username','disabled={!!flow.pending||flow.corrupt||!username')
out[str(p)]=v
print(json.dumps(out,ensure_ascii=True))
