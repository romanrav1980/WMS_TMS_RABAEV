import {useEffect,useRef,useState} from "react";
import {apiFetch,ApiRequestError,apiOperationScope} from "../../api";
type Command={operation_id:string;trip_id:number;warehouse_id:number;source_price_id:number;expected_norm_version:number;currency:string};
export function TransportCostConduct({trip,warehouse,source,version,currency,onRefresh}:{trip:number;warehouse:number;source:number;version:number;currency:string;onRefresh:()=>Promise<void>}){
 const key="nicora.transport-cost:"+apiOperationScope()+":"+trip+":"+warehouse+":"+source;
 const running=useRef(false),epoch=useRef(0);
 const [intent,setIntent]=useState<Command|null>(null),[blocked,setBlocked]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{
  epoch.current++;setIntent(null);setBlocked(false);setBusy(false);setMessage("");
  try{
   const raw=localStorage.getItem(key);
   if(raw!==null){
    const d=JSON.parse(raw) as Command;
    if(!d||Array.isArray(d)||Object.keys(d).length!==6||typeof d.operation_id!=="string"||!/^TCOST:[A-Za-z0-9-]+$/.test(d.operation_id)
      ||d.trip_id!==trip||d.warehouse_id!==warehouse||d.source_price_id!==source||!Number.isInteger(d.expected_norm_version)||d.expected_norm_version<1||!/^[A-Z]{3}$/.test(d.currency))throw Error("Нечитаемая сохранённая операция: требуется разбор исходного запроса.");
    setIntent(d);
   }
  }catch(e){setBlocked(true);setMessage(String(e));}
  return()=>{epoch.current++;};
 },[key,trip,warehouse,source]);
 async function conduct(){
  if(running.current||blocked)return;running.current=true;const current=epoch.current;setBusy(true);setMessage("");
  try{
   const body=intent??{operation_id:"TCOST:"+crypto.randomUUID(),trip_id:trip,warehouse_id:warehouse,source_price_id:source,expected_norm_version:version,currency};
   localStorage.setItem(key,JSON.stringify(body));setIntent(body);
   const result=await apiFetch<{operation_id:string;total:string;currency:string}>("/api/finance/logistics-costs/transport-costs/conduct",{method:"POST",body:JSON.stringify(body)});
   localStorage.removeItem(key);
   if(current===epoch.current){setIntent(null);setMessage("Проведено "+result.total+" "+result.currency+". Операция "+result.operation_id);}
  }catch(e){
   if(current===epoch.current)setMessage(String(e));
   if(e instanceof ApiRequestError&&e.confirmedRejection){
    try{await onRefresh();localStorage.removeItem(key);if(current===epoch.current)setIntent(null);}
    catch{if(current===epoch.current)setMessage("Отказ подтверждён, обновить исходные данные не удалось. Сохранён точный запрос.");}
   }
  }finally{running.current=false;if(current===epoch.current)setBusy(false);}
 }
 return <div><button type="button" title="Однократно записать нормативные транспортные расходы и финансовое исходящее сообщение" disabled={busy||blocked} onClick={()=>void conduct()}>{busy?"Проведение…":intent?"Повторить сохранённую операцию":"Провести нормативные затраты"}</button>
  {message&&<p role="status">{message}</p>}<p>Прежняя сумма счёта перевозчика не изменяется.</p></div>;
}
