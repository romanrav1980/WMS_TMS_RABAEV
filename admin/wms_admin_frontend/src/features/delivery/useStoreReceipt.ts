import {receiptResult,refreshReceiptCorrection,type ReceiptResult} from "./receiptResult";
import {parseReceiptIntent} from "./receiptIntentValidation";
import { useEffect, useRef, useState } from "react";
import { receiptBase, receiptRequest, ReceiptApiError } from "./api";
import type { StorePlace, StorePreview, PendingReceipt, ReceiptCredentials, StoreDisposition, WeightEvidence, StoreUnitScan, StoreAggregateScan, UnloadingDetails } from "./contracts";

export function useStoreReceipt(tripId: number, address: string, credentials: ReceiptCredentials) {
 const [places,setPlaces]=useState<StorePlace[]>([]),[preview,setPreview]=useState<StorePreview|null>(null);
 const [pending,setPending]=useState<PendingReceipt|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const key="store-receipt:"+receiptBase()+":"+credentials.username+":"+tripId+":"+address;
 const inFlight=useRef(false),loadedScope=useRef(""),corruptRef=useRef(false);
 const [corrupt,setCorrupt]=useState(false),[more,setMore]=useState(false),[stalePreview,setStalePreview]=useState(false),[lastReceipt,setLastReceipt]=useState<ReceiptResult|null>(null);
 const current=useRef(key);current.current=key;
 useEffect(()=>{
  loadedScope.current=key;setLastReceipt(null);setStalePreview(false);setPlaces([]);setMore(false);setPreview(null);setPending(null);setMessage("");
  try {setPending(parseReceiptIntent(localStorage.getItem(key),address));corruptRef.current=false;setCorrupt(false);}
  catch {corruptRef.current=true;setCorrupt(true);setMessage("Сохранённая операция повреждена. Новая отправка заблокирована; сохраните архив и перечитайте места.");}
 },[key]);
 async function loadPlaces(recover=false,append=false) {
  if(busy||inFlight.current||loadedScope.current!==key||(corruptRef.current&&!recover))return;
  const after=append?places[places.length-1]?.load_operation_id||"":"",scope=key,damaged=recover?localStorage.getItem(key):null;setBusy(true);
  try {
   if(recover){if(!corruptRef.current)throw Error("Черновик уже изменён.");localStorage.setItem("store-receipt-archive:"+scope+":"+crypto.randomUUID(),damaged||"");}
   const data=await receiptRequest<StorePlace[]>("/trips/"+tripId+"/places?store_address="+encodeURIComponent(address)+"&limit=100"+(after?"&after="+encodeURIComponent(after):""),credentials);
   if(current.current===scope){if(recover){if(localStorage.getItem(scope)!==damaged)throw Error("Черновик изменён другой вкладкой.");localStorage.removeItem(scope);corruptRef.current=false;setCorrupt(false);setPending(null);}
    setPlaces(rows=>append?[...rows,...data.filter(x=>!rows.some(old=>old.load_operation_id===x.load_operation_id))]:data);setMore(data.length===100);setMessage(data.length?"Выберите фактически доставленное место.":"Нет грузовых мест для этого адреса и получателя.");}
  }catch(error){if(current.current===scope)setMessage(String(error));}
  finally {setBusy(false);}
 }
 async function show(loadOperation: string) {
  if(busy||inFlight.current||loadedScope.current!==key||corruptRef.current)return;
  const scope=key;setBusy(true);setPreview(null);setStalePreview(false);
  try {
   const data=await receiptRequest<StorePreview>("/preview?load_operation_id="+encodeURIComponent(loadOperation)+"&store_address="+encodeURIComponent(address),credentials);
   if(current.current===scope){if(data.load_operation_id!==loadOperation||data.store_address!==address)throw Error("Ответ состава относится к другому месту или магазину.");setPreview(data);setMessage("");}
  }catch(error){if(current.current===scope)setMessage(String(error));}
  finally {setBusy(false);}
 }
 async function send(intent: PendingReceipt, scope: string) {
  if(busy||inFlight.current||loadedScope.current!==scope||current.current!==scope||corruptRef.current)return;let savedRaw:string|null=null;try{savedRaw=localStorage.getItem(scope);if(!savedRaw||JSON.stringify(parseReceiptIntent(savedRaw,address)?.body)!==JSON.stringify(intent.body))throw Error("Changed command");}catch{corruptRef.current=true;setCorrupt(true);setMessage("Сохранённая команда повреждена или изменена. Отправка заблокирована; перечитайте места.");return;}inFlight.current=true;setBusy(true);
  try {
   const data=receiptResult(await receiptRequest<unknown>("/confirm",credentials,intent.body),intent.body);
   if(localStorage.getItem(scope)!==savedRaw)throw Error("Черновик изменился во время запроса. Сервер ответил; перечитайте места.");
   localStorage.removeItem(scope);if(localStorage.getItem(scope)!==null)throw Error("Сервер подтвердил приёмку, но сохранённая команда не очищена. Повторите её с прежним номером.");
   if(current.current===scope){setLastReceipt(data);setPending(null);setPreview(null);setPlaces(rows=>rows.map(row=>row.load_operation_id===intent.body.load_operation_id?{...row,receipt_state:data.status}:row));setMessage("Приёмка подтверждена. "+data.operation_id);}
  }catch(error){
   if(current.current===scope&&localStorage.getItem(scope)===savedRaw){
    const saved={...intent,confirmedRejection:error instanceof ReceiptApiError&&error.confirmed};
    localStorage.setItem(scope,JSON.stringify(saved));setPending(saved);
    setMessage(String(error)+(saved.confirmedRejection?" Отказ подтверждён: можно исправить данные.":" Повторите сохранённую операцию."));
   }
  }finally {inFlight.current=false;setBusy(false);}
 }
 async function confirm(scan: string, cameras: boolean, observations?: StoreDisposition[], caseNote?: string, evidence?: WeightEvidence, scans?: StoreUnitScan[], unloading?: UnloadingDetails, aggregates?:StoreAggregateScan[]) {
  if(busy||inFlight.current||pending||!preview||stalePreview||loadedScope.current!==key||corruptRef.current)return;
  if(preview.store_address!==address){setMessage("Обновите состав для выбранного адреса.");return;}
  const intent:PendingReceipt={body:{operation_id:"STORE.RECEIPT:"+crypto.randomUUID(),load_operation_id:preview.load_operation_id,
   store_address:address,scan_place:scan,expected_composition_signature:preview.composition_signature,before_cameras:cameras,...(unloading?{unloading}:{}),...(observations?.length?{observations}:{}),...(caseNote?{case_note:caseNote}:{}),...evidence,...(scans?.length?{scans}:{}),...(aggregates?.length?{aggregation_scans:aggregates}:{})}};
  try {const wire=JSON.stringify(intent);localStorage.setItem(key,wire);if(localStorage.getItem(key)!==wire)throw Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");setPending(intent);await send(intent,key);}
  catch(error){setMessage(String(error));}
 }
 async function restart() {
  if(busy||inFlight.current||loadedScope.current!==key||!pending?.confirmedRejection)return;
  const scope=key,previous=preview;setBusy(true);
  try{const fresh=await refreshReceiptCorrection(scope,pending,address,credentials);if(current.current!==scope)return;
   if(localStorage.getItem(scope)!==fresh.raw)throw Error("Команда изменена другой вкладкой. Ввод сохранён.");localStorage.removeItem(scope);if(localStorage.getItem(scope)!==null)throw Error("Не удалось освободить подтверждённо отклонённую команду.");setPending(null);
   const changed=!previous||fresh.preview.composition_signature!==previous.composition_signature||fresh.preview.mode!==previous.mode||JSON.stringify(fresh.preview.marked_unit_control)!==JSON.stringify(previous.marked_unit_control);
   setStalePreview(changed);if(!changed)setPreview(fresh.preview);setMessage(changed?"Состав или правила изменились. Прежний ввод оставлен для сверки. Выберите место заново для новой формы; автоматического переноса нет.":"Отказ подтверждён. Исправьте данные: количества, фотографии и сканы сохранены. Состав перечитан с сервера.");
  }catch(error){if(current.current===scope)setMessage(String(error));}finally{setBusy(false);}
 }
 return {places,preview,pending,busy,message,corrupt,more,lastReceipt,stalePreview,next:()=>loadPlaces(false,true),recover:()=>loadPlaces(true),loadPlaces,show,confirm,retry:()=>pending?send(pending,key):Promise.resolve(),restart};
}
