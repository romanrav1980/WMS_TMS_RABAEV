import {tareResult} from "./tareResult";
import {useEffect,useRef,useState} from "react";
import {tareBase,tareRequest,TareApiError} from "./api";
import type {Credentials,TareBody,TareIntent,TareOffer,TareContext,TareDebt} from "./api";

export function useTare(tripId:number,credentials:Credentials){
 const key="tare:"+tareBase()+":"+credentials.username+":"+tripId;
 const current=useRef(key);current.current=key;
 const locked=useRef(false),intentRef=useRef<TareIntent|null>(null);
 const [debts,setDebts]=useState<TareDebt[]>([]);
 const [revision,setRevision]=useState(0),[storageBlocked,setStorageBlocked]=useState(false);
 const blockedRef=useRef(false);
 const [context,setContext]=useState<TareContext|null>(null);
 const [pending,setPending]=useState<TareIntent|null>(null),[busy,setBusy]=useState(false),[message,setMessage]=useState(""),[rows,setRows]=useState<TareOffer[]>([]);
 useEffect(()=>{current.current=key;setRows([]);setDebts([]);setContext(null);setMessage("");setStorageBlocked(false);blockedRef.current=false;try{const intent=JSON.parse(localStorage.getItem(key)||"null") as TareIntent|null;if(intent!==null&&(typeof intent!=="object"||Array.isArray(intent)||!intent.body||!["/offer","/accept","/damage","/writeoff","/loss-report"].includes(intent.path)||("task_id"in intent.body&&intent.body.task_id!==tripId)||typeof intent.body.operation_id!=="string"||! /^[A-Za-z0-9_.:-]{1,100}$/.test(intent.body.operation_id)||(intent.confirmed!==undefined&&typeof intent.confirmed!=="boolean")))throw new Error("Invalid saved intent");intentRef.current=intent;setPending(intent);}catch{intentRef.current=null;setPending(null);blockedRef.current=true;setStorageBlocked(true);setMessage("Сохранённая операция повреждена. Новые передачи заблокированы; исходная запись сохранена для разбора.");}},[key]);
 async function readContext(scope:string){
 const [data,options]=await Promise.all([tareRequest<TareOffer[]>("/trips/"+tripId+"/offers",credentials),tareRequest<TareContext>("/trips/"+tripId+"/context",credentials)]);if(current.current===scope){setRows(data);setContext(options);}
 }
 async function load(){
  if(locked.current||intentRef.current)return;const scope=key;locked.current=true;setBusy(true);
  try{await readContext(scope);}
  catch(e){if(current.current===scope)setMessage(String(e));}
  finally{locked.current=false;setBusy(false);}
 }
 async function loadDebt(wareId:number){
  if(locked.current||intentRef.current||!Number.isSafeInteger(wareId)||wareId<1)return;const scope=key;locked.current=true;setBusy(true);
  try{const data=await tareRequest<TareDebt[]>("/warehouses/"+wareId+"/store-debt",credentials);if(current.current===scope)setDebts(data);}
  catch(e){if(current.current===scope)setMessage(String(e));}finally{locked.current=false;setBusy(false);}
 }
 async function send(intent:TareIntent,scope:string){
  if(locked.current||blockedRef.current)return;locked.current=true;setBusy(true);
  try{const result=tareResult(await tareRequest<unknown>(intent.path,credentials,intent.body),intent);let removed=false;try{localStorage.removeItem(scope);removed=localStorage.getItem(scope)===null;}catch{removed=false;}
   // Подтверждённая операция, запись которой не удалилась, блокирует новые команды: повтор того же ID безопасен, новая — нет.
   if(!removed){blockedRef.current=true;setStorageBlocked(true);}
   if(current.current===scope){intentRef.current=null;setPending(null);setRows([]);setDebts([]);setRevision(v=>v+1);setMessage(intent.path==="/loss-report"?"Недостача зарегистрирована. Спорная тара недоступна до независимого решения.":intent.path==="/damage"?"Повреждение зафиксировано; общий баланс тары сохранён.":intent.path==="/writeoff"?"Списание проведено: "+result.quantity+" ед. повреждённой тары исключено из баланса. Товар не затронут.":result.status==="POSTED"?"Приёмка тары проведена. Количество у получателя: "+result.destination_quantity+". Непринятое: "+result.short_quantity+".":"Передача предложена. До приёмки другого участника тара остаётся у отправителя.");
    if(!removed)setMessage(m=>m+" Запись операции на устройстве удалить не удалось: новые операции заблокированы до проверки хранилища браузера.");
    try{await readContext(scope);}catch{if(current.current===scope){setContext(null);setMessage("Операция подтверждена. Не удалось обновить список — нажмите «Показать передачи этого рейса».");}}}}
  catch(e){if(current.current===scope){const saved={...intent,confirmed:e instanceof TareApiError&&e.confirmed};intentRef.current=saved;setPending(saved);try{localStorage.setItem(scope,JSON.stringify(saved));}catch{setMessage("Сохранено в памяти. Не закрывайте страницу.");}setMessage(String(e));}}
  finally{locked.current=false;setBusy(false);}
 }
 async function confirm(path:TareIntent["path"],payload:Omit<TareBody,"operation_id">){
  if(locked.current||intentRef.current||blockedRef.current)return;
  const quantity=payload.quantity??payload.accepted_quantity;
  if((path==="/damage"||path==="/writeoff"||path==="/loss-report")&&(!payload.reason||!payload.decision_reference)){setMessage("Укажите причину и номер акта или решения.");return;}
  if(typeof quantity!=="string"||! /^[0-9]{1,18}$/.test(quantity)||/^0+$/.test(quantity)||(path!=="/damage"&&path!=="/writeoff"&&path!=="/loss-report"&&!payload.scan_vehicle)){setMessage("Укажите целое положительное количество и скан машины.");return;}
  const intent:TareIntent={path,body:{...payload,operation_id:"TARE:"+crypto.randomUUID()}};
  // Команда отправляется, только если намерение записано и читается обратно без искажений.
  try{const raw=JSON.stringify(intent);localStorage.setItem(key,raw);if(localStorage.getItem(key)!==raw)throw Error("readback");}catch{setMessage("Операция не отправлена: не удалось надёжно сохранить её на этом устройстве.");return;}
  intentRef.current=intent;setPending(intent);await send(intent,key);
 }
 function restart(){if(!locked.current&&intentRef.current?.confirmed){localStorage.removeItem(key);intentRef.current=null;setPending(null);setRows([]);setContext(null);setMessage("Обновите передачи и исправьте данные.");}}
 return{rows,debts,loadDebt,context,pending,busy,message,revision,storageBlocked,load,confirm,restart,retry:()=>intentRef.current?send(intentRef.current,key):Promise.resolve()};
}
