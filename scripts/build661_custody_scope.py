import json
from pathlib import Path
p=Path("admin/wms_admin_frontend/src/features/delivery/useReturnCustody.ts")
s=p.read_text(encoding="utf-8")
s=s.replace('const locked=useRef(false),pendingRef=useRef<CustodyIntent|null>(null),corruptRef=useRef<string|null>(null);','const locked=useRef(false),pendingRef=useRef<CustodyIntent|null>(null),corruptRef=useRef<string|null>(null),loadedScope=useRef<string|null>(null);')
s=s.replace('setStoreRows([]);setDriverRows([]);setMessage("");\n  try','loadedScope.current=key;setStoreRows([]);setDriverRows([]);setMessage("");\n  try')
s=s.replace('if(locked.current||pendingRef.current||(corruptRef.current&&!recover))return;','if(loadedScope.current!==key||locked.current||pendingRef.current||(corruptRef.current&&!recover))return;')
s=s.replace('if(locked.current)return;locked.current=true;setBusy(true);','if(loadedScope.current!==scope||current.current!==scope||locked.current)return;locked.current=true;setBusy(true);')
s=s.replace('if(locked.current||pendingRef.current||corruptRef.current)return;','if(loadedScope.current!==key||locked.current||pendingRef.current||corruptRef.current)return;')
s=s.replace('if(!locked.current&&pendingRef.current?.confirmedRejection){localStorage.removeItem(key);','if(loadedScope.current===key&&!locked.current&&pendingRef.current?.confirmedRejection){\n   try{localStorage.removeItem(key);}catch{setMessage("Не удалось удалить подтверждённый отказ. Исходная операция сохранена.");return;}')
s=s.replace('return {storeRows,driverRows,pending,corrupt,busy,message,','const scopeReady=loadedScope.current===key;\n return {storeRows:scopeReady?storeRows:[],driverRows:scopeReady?driverRows:[],pending:scopeReady?pending:null,corrupt:scopeReady?corrupt:false,busy:busy||!scopeReady,message:scopeReady?message:"Загрузка сохранённой операции выбранного пользователя…",')
print(json.dumps({str(p):s}))
