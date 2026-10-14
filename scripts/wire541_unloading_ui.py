import json
from pathlib import Path
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/contracts.ts");v=p.read_text(encoding="utf-8")
v='''export interface UnloadingDetails {start_operation_id:string;method:"ROLL_CAGE"|"PALLET"|"MANUAL";rolling_difficult:boolean;loader_present:boolean;evidence_reference:string}
export interface UnloadingFact {operation_id:string;started_at_instant:string;status:"STARTED"|"COMPLETED";finished_at_instant?:string|null;actual_details?:UnloadingDetails|null}
export interface UnloadingStartBody {operation_id:string;load_operation_id:string;store_address:string;expected_composition_signature:string;scan_place:string;before_cameras:boolean}
'''+v
v=v.replace("export interface StorePreview {","export interface StorePreview {\n unloading?:UnloadingFact|null;")
v=v.replace("export interface ReceiptBody {","export interface ReceiptBody {\n unloading?:UnloadingDetails;")
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");v=p.read_text(encoding="utf-8")
v=v.replace("StoreUnitScan }","StoreUnitScan, UnloadingDetails }")
v=v.replace('credentials.username.trim().toLowerCase()','credentials.username')
v=v.replace("scans?: StoreUnitScan[]) {","scans?: StoreUnitScan[], unloading?: UnloadingDetails) {")
v=v.replace('before_cameras:cameras,...(observations','before_cameras:cameras,...(unloading?{unloading}:{}),...(observations')
out[str(p)]=v
out["admin/wms_admin_frontend/src/features/delivery/StoreUnloadingPanel.tsx"]='''import {useEffect,useRef,useState} from "react";
import {receiptBase,receiptRequest,ReceiptApiError} from "./api";
import type {StorePreview,ReceiptCredentials,UnloadingDetails,UnloadingStartBody} from "./contracts";
type Pending={body:UnloadingStartBody;confirmedRejection?:boolean};
export function StoreUnloadingPanel({preview,credentials,scan,cameras,disabled,onDetails,onPending,onStarted}:{
 preview:StorePreview;credentials:ReceiptCredentials;scan:string;cameras:boolean;disabled:boolean;
 onDetails:(details:UnloadingDetails|undefined)=>void;onPending:(pending:boolean)=>void;onStarted:()=>Promise<void>}){
 const scope="store-unloading:"+receiptBase()+":"+credentials.username+":"+preview.load_operation_id+":"+preview.store_address;
 const current=useRef(scope);current.current=scope;
 const [pending,setPending]=useState<Pending|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const [method,setMethod]=useState<UnloadingDetails["method"]|"">(""),[difficult,setDifficult]=useState(false),[loader,setLoader]=useState(false),[reference,setReference]=useState("");
 useEffect(()=>{
  try{
   const saved=JSON.parse(localStorage.getItem(scope)||"null")as Pending|null;
   if(saved&&(saved.body.load_operation_id!==preview.load_operation_id||saved.body.store_address!==preview.store_address))throw new Error("Сохранённая операция другого места.");
   setPending(saved);onPending(!!saved);
  }catch(e){setMessage(String(e));setPending(null);onPending(true);}
  return()=>{current.current="";};
 },[scope]);
 useEffect(()=>{
  const start=preview.unloading;
  onDetails(start?.status==="STARTED"&&method&&reference.trim()?{start_operation_id:start.operation_id,method,rolling_difficult:difficult,loader_present:loader,evidence_reference:reference}:undefined);
 },[preview.unloading,method,difficult,loader,reference,onDetails]);
 async function send(intent:Pending){
  if(busy||disabled)return;const key=scope;setBusy(true);setMessage("");
  try{
   await receiptRequest("/unloading/start",credentials,intent.body);
   localStorage.removeItem(key);
   if(current.current===key){setPending(null);onPending(false);setMessage("Начало выгрузки сохранено.");await onStarted();}
  }catch(e){
   if(current.current===key){
    const saved={...intent,confirmedRejection:e instanceof ReceiptApiError&&e.confirmed};
    localStorage.setItem(key,JSON.stringify(saved));setPending(saved);onPending(true);setMessage(String(e));
   }
  }finally{if(current.current===key)setBusy(false);}
 }
 async function start(){
  if(pending||preview.already_received||!scan||!cameras||disabled)return;
  const intent:Pending={body:{operation_id:"UNLOAD.START:"+crypto.randomUUID(),load_operation_id:preview.load_operation_id,
   store_address:preview.store_address,expected_composition_signature:preview.composition_signature,scan_place:scan,before_cameras:cameras}};
  try{localStorage.setItem(scope,JSON.stringify(intent));setPending(intent);onPending(true);await send(intent);}
  catch(e){setMessage("Не удалось сохранить операцию до отправки: "+String(e));}
 }
 function reset(){
  if(!busy&&pending?.confirmedRejection){localStorage.removeItem(scope);setPending(null);onPending(false);setMessage("Исправьте скан и повторите начало новой операцией.");}
 }
 const fact=preview.unloading;
 return <section aria-label="Фактическая выгрузка"><h3>Выгрузка</h3>
  {fact?<p>Начало: {fact.started_at_instant}. {fact.status==="COMPLETED"?"Выгрузка завершена.":"Выгрузка начата; заполните фактические условия."}</p>:
   !preview.already_received&&<button type="button" title="Сохранить время начала выгрузки после сканирования места перед камерами" disabled={disabled||busy||!!pending||!scan||!cameras} onClick={()=>void start()}>Начать выгрузку</button>}
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
  {message&&<p role="status">{message}</p>}
 </section>;
}
'''
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreReceiptPanel.tsx");v=p.read_text(encoding="utf-8")
v='import {StoreUnloadingPanel} from "./StoreUnloadingPanel";\nimport type {UnloadingDetails} from "./contracts";\n'+v
v=v.replace(' const preview=flow.preview;', ' const preview=flow.preview;\n const [unloading,setUnloading]=useState<UnloadingDetails|undefined>(),[unloadPending,setUnloadPending]=useState(false);')
needle='    <StoreAdmissionPanel key='
assert needle in v
v=v.replace(needle,'''    <StoreUnloadingPanel key={username+":"+preview.load_operation_id+":"+preview.store_address} preview={preview} credentials={{username,password}} scan={scan} cameras={cameras} disabled={flow.busy||!!flow.pending}
      onDetails={setUnloading} onPending={setUnloadPending} onStarted={()=>flow.show(preview.load_operation_id)}/>
    <StoreAdmissionPanel key=''')
v=v.replace('disabled={flow.busy||!scan||!cameras||!!flow.pending}', 'disabled={flow.busy||!scan||!cameras||!!flow.pending||unloadPending||(preview.unloading?.status==="STARTED"&&!unloading)}')
v=v.replace('flow.confirm(scan,cameras,rows,note,evidence,scans)', 'flow.confirm(scan,cameras,rows,note,evidence,scans,unloading)')
out[str(p)]=v
print(json.dumps(out))
