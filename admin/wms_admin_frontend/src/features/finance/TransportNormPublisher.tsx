import {useEffect,useRef,useState} from "react";
import {apiFetch,apiOperationScope,ApiRequestError} from "../../api";

export type TransportNorm={unload_charge_basis?:"POINT"|"PLACE";pallet_unload_rate?:string;source:{vehicle_rate:string;hour_rate:string;point_rate:string};version:number;currency:string;effective_from:string;timezone_region:string;vehicle_size_class:string;rolling_unload_rate:string;manual_unload_rate:string;loader_rate:string};
type Fields={unload_charge_basis:string;pallet_unload_rate:string;currency:string;effective_from:string;timezone_region:string;vehicle_size_class:string;rolling_unload_rate:string;manual_unload_rate:string;loader_rate:string;reason:string;decision_reference:string};
type Body=Fields&{operation_id:string;warehouse_id:number;source_price_id:number;vehicle_type:string;expected_version:number};
type Pending={body:Body;rejected?:boolean};
const rate=/^[0-9]{1,18}(\.[0-9]{1,9})?$/;
const labels:Record<keyof Fields,string>={unload_charge_basis:"Единица начисления выгрузки",pallet_unload_rate:"Выгрузка паллеты",currency:"Валюта",effective_from:"Действует с",timezone_region:"Часовой пояс",vehicle_size_class:"Класс размера машины",rolling_unload_rate:"Выгрузка тележки",manual_unload_rate:"Ручная выгрузка",loader_rate:"Дополнительный грузчик",reason:"Причина изменения",decision_reference:"Основание утверждения"};
export function TransportNormPublisher({warehouse,source,vehicleType,norm,onPublished}:{warehouse:number;source:number;vehicleType:string;norm:TransportNorm|null;onPublished:()=>Promise<void>}){
 const scope="transport-norm:"+apiOperationScope()+":"+warehouse+":"+source;
 const current=useRef(scope);current.current=scope;const inFlight=useRef(false);
 const [fields,setFields]=useState<Fields>({unload_charge_basis:"",pallet_unload_rate:"",currency:"",effective_from:"",timezone_region:"",vehicle_size_class:"",rolling_unload_rate:"",manual_unload_rate:"",loader_rate:"",reason:"",decision_reference:""});
 const [pending,setPending]=useState<Pending|null>(null),[blocked,setBlocked]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{
  setFields({unload_charge_basis:norm?.unload_charge_basis||"",pallet_unload_rate:norm?.pallet_unload_rate||"",currency:norm?.currency||"",effective_from:norm?.effective_from||"",timezone_region:norm?.timezone_region||"",vehicle_size_class:norm?.vehicle_size_class||"",rolling_unload_rate:norm?.rolling_unload_rate||"",manual_unload_rate:norm?.manual_unload_rate||"",loader_rate:norm?.loader_rate||"",reason:"",decision_reference:""});
 },[scope,norm?.version]);
 useEffect(()=>{
  setPending(null);setBlocked(false);setMessage("");
  try{
   const saved=JSON.parse(localStorage.getItem(scope)||"null")as Pending|null;
   if(saved!==null){const b=saved.body;
    if(!b||b.warehouse_id!==warehouse||b.source_price_id!==source||typeof b.operation_id!=="string"
     ||! /^[A-Za-z0-9_.:-]{1,100}$/.test(b.operation_id)||!Number.isInteger(b.expected_version)||b.expected_version<0
     ||Object.keys(labels).filter(k=>k!=="unload_charge_basis"&&k!=="pallet_unload_rate").some(k=>typeof b[k as keyof Fields]!=="string")
     ||typeof b.vehicle_type!=="string"||!b.vehicle_type
     ||(saved.rejected!==undefined&&typeof saved.rejected!=="boolean"))throw new Error("Повреждена сохранённая операция. Сохраните запись для разбора; новая публикация заблокирована.");
   }
   setPending(saved);
  }catch(e){setBlocked(true);setMessage(String(e));}
  return()=>{current.current="";};
 },[scope]);
 async function send(intent:Pending){
  if(inFlight.current||blocked)return;inFlight.current=true;setBusy(true);const key=scope;
  try{
   const result=await apiFetch<TransportNorm>("/api/finance/logistics-costs/transport-norms",{method:"POST",body:JSON.stringify(intent.body)});
   localStorage.removeItem(key);
   if(current.current===key){
    setPending(null);setMessage(`Опубликована версия ${result.version}, ${result.currency}, с ${result.effective_from}.`);
    try{await onPublished();}catch(e){if(current.current===key)setMessage(`Версия ${result.version} опубликована. Обновить список не удалось: `+String(e));}
   }
  }catch(e){if(current.current===key){
   const saved={...intent,rejected:e instanceof ApiRequestError&&e.confirmedRejection};setPending(saved);
   try{localStorage.setItem(key,JSON.stringify(saved));}catch{setBlocked(true);}
   setMessage(String(e)+(saved.rejected?" Сервер подтвердил отказ.":" Результат не подтверждён. Повторите сохранённую операцию."));
  }}finally{inFlight.current=false;if(current.current===key)setBusy(false);}
 }
 async function publish(event:React.FormEvent){
  event.preventDefault();if(busy||inFlight.current||pending||blocked)return;
  if(!["POINT","PLACE"].includes(fields.unload_charge_basis)||!/^[A-Z]{3}$/.test(fields.currency)||![fields.rolling_unload_rate,fields.manual_unload_rate,fields.loader_rate,fields.pallet_unload_rate].every(v=>rate.test(v))){setMessage("Укажите валюту из трёх заглавных букв и точные неотрицательные ставки через точку.");return;}
  const intent:Pending={body:{...fields,operation_id:"TRANSPORT.NORM:"+crypto.randomUUID(),warehouse_id:warehouse,source_price_id:source,vehicle_type:String(vehicleType),expected_version:norm?.version||0}};
  try{localStorage.setItem(scope,JSON.stringify(intent));setPending(intent);await send(intent);}
  catch(e){setMessage("Не удалось сохранить операцию до отправки: "+String(e));}
 }
 async function reset(){
  if(busy||!pending?.rejected)return;
  try{await onPublished();if(current.current!==scope)return;localStorage.removeItem(scope);setPending(null);setMessage("Обновите поля для новой редакции.");}
  catch(e){setMessage(String(e));}
 }
 return <details><summary title="Опубликовать редакцию нормы существующего транспортного тарифа">Настроить транспортную норму</summary>
  <p>Исходный тариф {source}; текущая версия {norm?.version||0}. Публикация сохраняет текущие ставки автомобиля, часа и точки вместе с указанными условиями.</p>
  <form onSubmit={e=>void publish(e)}><fieldset disabled={busy||!!pending||blocked}>
   {(Object.keys(labels)as Array<keyof Fields>).map(k=><label key={k} title={labels[k]+" для новой редакции транспортной нормы"}>{labels[k]}{k==="unload_charge_basis"?<select required title="Выберите начисление один раз за адрес или за каждое физическое место" value={fields[k]} onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}><option value="">Выберите единицу</option><option value="POINT">За обслуженный адрес</option><option value="PLACE">За физическое место</option></select>:<input required type={k==="effective_from"?"date":"text"} value={fields[k]} maxLength={k==="reason"?500:k==="decision_reference"?60:k==="timezone_region"?64:k==="currency"?3:40} onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}/>}</label>)}
   <button type="submit" title="Сохранить новую версию нормы через Oracle с проверкой текущей версии">Опубликовать новую версию</button>
  </fieldset></form>
  {pending&&<p>Операция {pending.body.operation_id}, ожидаемая версия {pending.body.expected_version}.<button type="button" title="Повторить неизменённое сообщение с тем же идентификатором" disabled={busy||blocked} onClick={()=>void send(pending)}>Повторить сохранённую публикацию</button></p>}
  {pending?.rejected&&<button type="button" title="Обновить исходную версию после подтверждённого отказа и разрешить исправление формы" disabled={busy} onClick={()=>void reset()}>Исправить после отказа</button>}
  {message&&<p role="status">{message}</p>}
 </details>;
}
