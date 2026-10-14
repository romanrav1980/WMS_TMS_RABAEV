import { useEffect,useRef,useState } from "react";
import { receiptBase,ReceiptApiError } from "./api";
import { parseCustodyIntent } from "./custodyIntentValidation";
import { custodyRequest } from "./custodyApi";
import type { CustodyBody,CustodyPayload,CustodyIntent,ReturnDriverPlace,ReturnStorePlace } from "./custodyApi";
import type { ReceiptCredentials } from "./contracts";

export function useReturnCustody(tripId:number,address:string,mode:"store"|"driver",credentials:ReceiptCredentials){
 const key="return-custody:"+receiptBase()+":"+credentials.username+":"+tripId+":"+address+":"+mode;
 const current=useRef(key);current.current=key;
 const locked=useRef(false),pendingRef=useRef<CustodyIntent|null>(null),corruptRef=useRef<string|null>(null),loadedScope=useRef<string|null>(null);
 const [corrupt,setCorrupt]=useState(false);
 const [pending,setPending]=useState<CustodyIntent|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const [storeRows,setStoreRows]=useState<ReturnStorePlace[]>([]),[driverRows,setDriverRows]=useState<ReturnDriverPlace[]>([]);
 useEffect(()=>{
  loadedScope.current=key;setStoreRows([]);setDriverRows([]);setMessage("");
  try{const saved=parseCustodyIntent(localStorage.getItem(key));pendingRef.current=saved;setPending(saved);corruptRef.current=null;setCorrupt(false);}
  catch{pendingRef.current=null;setPending(null);corruptRef.current=key;setCorrupt(true);setMessage("Сохранённая операция повреждена. Отправка заблокирована; сохраните архив и перечитайте передачи.");}
 },[key]);
 async function load(recover=false){
  if(loadedScope.current!==key||locked.current||pendingRef.current||(corruptRef.current&&!recover))return;const scope=key;locked.current=true;setBusy(true);
  try{
   const damaged=recover?localStorage.getItem(scope):null;
   if(recover){if(corruptRef.current!==scope)throw Error("Сначала выберите повреждённый черновик.");localStorage.setItem("return-custody-archive:"+scope+":"+crypto.randomUUID(),damaged||"");}
   if(mode==="store"){const rows=await custodyRequest<ReturnStorePlace[]>("/store?store_address="+encodeURIComponent(address)+"&task_id="+tripId,credentials);if(current.current===scope){setStoreRows(rows.filter(row=>row.tt_id===tripId));setDriverRows([]);}}
   else{const rows=await custodyRequest<ReturnDriverPlace[]>("/driver?task_id="+tripId,credentials);if(current.current===scope){setDriverRows(rows.filter(row=>row.tt_id===tripId));setStoreRows([]);}}
   if(current.current===scope){
    if(recover){if(localStorage.getItem(scope)!==damaged)throw Error("Черновик изменён другой вкладкой. Повторите восстановление.");localStorage.removeItem(scope);corruptRef.current=null;setCorrupt(false);}
    setMessage(recover?"Повреждённый черновик сохранён в архив. Перечитаны только ещё не подтверждённые передачи.":"");
   }
  }catch(error){if(current.current===scope)setMessage(String(error));}
  finally{locked.current=false;setBusy(false);}
 }
 async function send(intent:CustodyIntent,scope:string){
  if(loadedScope.current!==scope||current.current!==scope||locked.current)return;locked.current=true;setBusy(true);
  try{
   const result=await custodyRequest<{operation_id:string;custody:string}>(intent.path,credentials,intent.body);
   localStorage.removeItem(scope);
   if(current.current===scope){pendingRef.current=null;setPending(null);setStoreRows([]);setDriverRows([]);setMessage(result.custody==="VEHICLE"?"Возврат принят водителем. Ответственность остаётся у машины до приёмки складом.":"Передача магазина подтверждена. Водитель должен отдельно принять возврат.");}
  }catch(error){
   if(current.current===scope){const saved={...intent,confirmedRejection:error instanceof ReceiptApiError&&error.confirmed};pendingRef.current=saved;setPending(saved);
    try{localStorage.setItem(scope,JSON.stringify(saved));}catch{setMessage("Операция сохранена в памяти. Не закрывайте страницу.");}
    setMessage(String(error)+(saved.confirmedRejection?" Отказ подтверждён.":" Повторите сохранённую операцию."));}
  }finally{locked.current=false;setBusy(false);}
 }
 async function confirm(path:CustodyIntent["path"],body:CustodyPayload){
  if(loadedScope.current!==key||locked.current||pendingRef.current||corruptRef.current)return;
  if("quantity" in body&&(!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(body.quantity)||!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(body.gross_weight_kg)||!body.pallet_identifier||body.pallet_identifier.length>200)){setMessage("Заполните идентификатор паллеты, точное количество и массу.");return;}
  if("scan_vehicle" in body&&(!body.scan_vehicle||body.scan_vehicle.length>50||!body.scan_pallet||body.scan_pallet.length>200)){setMessage("Укажите сканы машины и паллеты.");return;}
  const intent:CustodyIntent={path,body:{...body,operation_id:"RETURN.CUSTODY:"+crypto.randomUUID()} as CustodyBody};
  try{localStorage.setItem(key,JSON.stringify(intent));}
  catch{setMessage("Операция не отправлена: не удалось сохранить исходное согласование.");return;}
  pendingRef.current=intent;setPending(intent);await send(intent,key);
 }
 function restart(){
  if(loadedScope.current===key&&!locked.current&&pendingRef.current?.confirmedRejection){
   try{localStorage.removeItem(key);}catch{setMessage("Не удалось удалить подтверждённый отказ. Исходная операция сохранена.");return;}pendingRef.current=null;setPending(null);setStoreRows([]);setDriverRows([]);setMessage("Обновите исходный возврат и исправьте данные.");}
 }
 const scopeReady=loadedScope.current===key;
 return {storeRows:scopeReady?storeRows:[],driverRows:scopeReady?driverRows:[],pending:scopeReady?pending:null,corrupt:scopeReady?corrupt:false,busy:busy||!scopeReady,message:scopeReady?message:"Загрузка сохранённой операции выбранного пользователя…",load:()=>load(),recoverCorrupt:()=>load(true),confirm,restart,retry:()=>pendingRef.current?send(pendingRef.current,key):Promise.resolve()};
}
