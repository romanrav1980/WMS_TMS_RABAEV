import {useEffect,useRef,useState} from "react";
import {receiptBase,receiptRequest,ReceiptApiError} from "./api";
import type {StorePreview,ReceiptCredentials,UnloadingDetails,UnloadingStartBody} from "./contracts";
type Pending={body:UnloadingStartBody;confirmedRejection?:boolean};
export function StoreUnloadingPanel({preview,credentials,scan,cameras,disabled,onDetails,onPending,onStarted}:{
 preview:StorePreview;credentials:ReceiptCredentials;scan:string;cameras:boolean;disabled:boolean;
 onDetails:(details:UnloadingDetails|undefined)=>void;onPending:(pending:boolean)=>void;onStarted:()=>Promise<void>}){
 const scope="store-unloading:"+receiptBase()+":"+credentials.username+":"+preview.load_operation_id+":"+preview.store_address;
 const inFlight=useRef(false);
 const current=useRef(scope);current.current=scope;
 const [pending,setPending]=useState<Pending|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const [damagedIntent,setDamagedIntent]=useState(false);
 const [method,setMethod]=useState<UnloadingDetails["method"]|"">(""),[difficult,setDifficult]=useState(false),[loader,setLoader]=useState(false),[reference,setReference]=useState("");
 useEffect(()=>{
  current.current=scope;
  setMessage("");setDamagedIntent(false);setMethod("");setDifficult(false);setLoader(false);setReference("");
  try{
   const saved=JSON.parse(localStorage.getItem(scope)||"null")as Pending|null;
   if(saved!==null){
    const body=saved.body;
    if(!body||typeof body.operation_id!=="string"||! /^[A-Za-z0-9_.:-]{1,100}$/.test(body.operation_id)
     ||body.load_operation_id!==preview.load_operation_id||body.store_address!==preview.store_address
     ||typeof body.expected_composition_signature!=="string"||!body.expected_composition_signature
     ||typeof body.scan_place!=="string"||!body.scan_place||body.before_cameras!==true
     ||(saved.confirmedRejection!==undefined&&typeof saved.confirmedRejection!=="boolean"))throw new Error("Сохранённая операция повреждена или относится к другому месту.");
   }
   setPending(saved);onPending(!!saved);
  }catch(e){setMessage(String(e));setPending(null);setDamagedIntent(true);onPending(true);}
  return()=>{current.current="";};
 },[scope]);
 useEffect(()=>{
  const start=preview.unloading;
  onDetails(start?.status==="STARTED"&&method&&reference.trim()&&(!difficult||loader)?{start_operation_id:start.operation_id,method,rolling_difficult:difficult,loader_present:loader,evidence_reference:reference}:undefined);
 },[preview.unloading,method,difficult,loader,reference,onDetails]);
 async function send(intent:Pending){
  if(busy||inFlight.current||disabled)return;inFlight.current=true;const key=scope;setBusy(true);setMessage("");
  try{
   await receiptRequest("/unloading/start",credentials,intent.body);
   localStorage.removeItem(key);
   if(current.current===key){setPending(null);onPending(false);setMessage("Начало выгрузки сохранено.");await onStarted();}
  }catch(e){
   if(current.current===key){
    const saved={...intent,confirmedRejection:e instanceof ReceiptApiError&&e.confirmed};
    localStorage.setItem(key,JSON.stringify(saved));setPending(saved);onPending(true);setMessage(String(e));
   }
  }finally{inFlight.current=false;if(current.current===key)setBusy(false);}
 }
 async function start(){
  if(pending||damagedIntent||inFlight.current||preview.already_received||!scan||!cameras||disabled)return;
  const intent:Pending={body:{operation_id:"UNLOAD.START:"+crypto.randomUUID(),load_operation_id:preview.load_operation_id,
   store_address:preview.store_address,expected_composition_signature:preview.composition_signature,scan_place:scan,before_cameras:cameras}};
  try{localStorage.setItem(scope,JSON.stringify(intent));setPending(intent);onPending(true);await send(intent);}
  catch(e){setMessage("Не удалось сохранить операцию до отправки: "+String(e));}
 }
 function reset(){
  if(!busy&&pending?.confirmedRejection){localStorage.removeItem(scope);setPending(null);onPending(false);setMessage("Исправьте скан и повторите начало новой операцией.");}
 }
 async function recover(){
  if(busy||inFlight.current)return;
  const key=scope;inFlight.current=true;setBusy(true);
  try{
   const raw=localStorage.getItem(key);
   if(raw!==null)localStorage.setItem(key+":damaged:"+crypto.randomUUID(),raw);
   await receiptRequest<StorePreview>("/preview?load_operation_id="+encodeURIComponent(preview.load_operation_id)+"&store_address="+encodeURIComponent(preview.store_address),credentials);
   if(current.current!==key)return;
   // The load has one server-side start. Refresh before allowing any new intent.
   if(localStorage.getItem(key)!==raw)throw new Error("Локальная запись изменилась. Обновите страницу перед восстановлением.");
   localStorage.removeItem(key);setDamagedIntent(false);setPending(null);onPending(false);
   setMessage("Исходная запись сохранена в локальном архиве. Состояние выгрузки перечитано с сервера.");
   await onStarted();
  }catch(e){if(current.current===key)setMessage("Восстановление не завершено: "+String(e));}
  finally{inFlight.current=false;if(current.current===key)setBusy(false);}
 }
 const fact=preview.unloading;
 return <section aria-label="Фактическая выгрузка"><h3>Выгрузка</h3>
  {fact?<p>Начало: {fact.started_at_instant}. {fact.status==="COMPLETED"?"Выгрузка завершена.":"Выгрузка начата; заполните фактические условия."}</p>:
   !preview.already_received&&<button type="button" title="Сохранить время начала выгрузки после сканирования места перед камерами" disabled={disabled||busy||!!pending||damagedIntent||!scan||!cameras} onClick={()=>void start()}>Начать выгрузку</button>}
  {fact?.status==="STARTED"&&<fieldset disabled={disabled||busy||!!pending}>
   <label title="Укажите фактический способ выгрузки"><span>Способ выгрузки</span><select value={method} onChange={e=>{setMethod(e.target.value as typeof method);setDifficult(false);setLoader(false);}}><option value="">Выберите способ</option><option value="MANUAL">Вручную</option><option value="PALLET">Паллетой</option><option value="ROLL_CAGE">Закатывание тележки</option></select></label>
   <label title="Отметьте фактическое затруднение закатывания"><input type="checkbox" disabled={method!=="ROLL_CAGE"} checked={difficult} onChange={e=>setDifficult(e.target.checked)}/>Закатывание затруднено</label>
   <label title="Подтвердите фактическое участие грузчика"><input type="checkbox" checked={loader} onChange={e=>setLoader(e.target.checked)}/>Работал грузчик</label>
   <label title="Укажите ссылку на акт, фото или запись подтверждения условий выгрузки">Основание подтверждения<input maxLength={100} value={reference} onChange={e=>setReference(e.target.value)}/></label>
   {difficult&&!loader&&<p role="alert">Для затруднённого закатывания подтвердите участие грузчика.</p>}
   <p>Условия сохранятся вместе с приёмкой. Начисление расходов выполняется отдельно.</p>
  </fieldset>}
  {pending&&<button type="button" title="Повторить точную сохранённую операцию начала" disabled={disabled||busy} onClick={()=>void send(pending)}>Повторить сохранённое начало</button>}
  {pending?.confirmedRejection&&<button type="button" title="Отказ подтверждён сервером; можно исправить данные" disabled={busy} onClick={reset}>Исправить после отказа</button>}
  {damagedIntent&&<button type="button" title="Сохранить повреждённую запись в архиве и получить фактическое состояние выгрузки с сервера" disabled={busy} onClick={()=>void recover()}>Восстановить состояние выгрузки</button>}
  {message&&<p role="status">{message}</p>}
 </section>;
}
