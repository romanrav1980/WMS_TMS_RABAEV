import { useEffect,useRef,useState } from "react";
import { receiptBase } from "./api";
import type { ReceiptCredentials,StorePreview } from "./contracts";
type Capture={capture_key:string;device_id:string;gross_weight_kg:string;received_at:string;sample_count:number;span_ms:number;calibration_ref:string};
export function StoreScalePanel({preview,credentials,selected="",onSelect}:{preview:StorePreview;credentials:ReceiptCredentials;selected?:string;onSelect?:(key:string)=>void}) {
 const [items,setItems]=useState<Capture[]>([]),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const current=useRef("");const scope=credentials.username+":"+preview.load_operation_id+":"+preview.store_address;current.current=scope;
 useEffect(()=>{current.current=scope;return()=>{current.current="";};},[scope]);
 async function load(){
  if(busy)return;const selected=scope;setBusy(true);setItems([]);setMessage("");
  try {
   const params=new URLSearchParams({load_operation_id:preview.load_operation_id,store_address:preview.store_address});
   const response=await fetch(receiptBase()+"/api/delivery/store-scales/captures?"+params,{headers:{Authorization:"Basic "+btoa(credentials.username+":"+credentials.password)}});
   const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==="string"?data.detail:data.detail?.message||"Не удалось получить измерения");
   if(current.current===selected){setItems(data.items);setMessage(data.items.length?"":"Устойчивого показания шлюза для этого места пока нет.");}
  }catch(error){if(current.current===selected)setMessage(String(error));}finally{setBusy(false);}
 }
 return <section><h3>Показания весов</h3>
  <button disabled={busy} onClick={()=>void load()}>Показать архивированные измерения</button>
  {items.map(item=><p key={item.capture_key}>{onSelect&&<label><input type="radio" name={"capture:"+scope} value={item.capture_key} checked={selected===item.capture_key} onChange={()=>onSelect(item.capture_key)}/>Выбрать измерение</label>}{item.gross_weight_kg} кг брутто · {item.device_id} · {item.received_at} · {item.sample_count} отсчётов за {item.span_ms} мс · калибровка {item.calibration_ref}</p>)}
  <p>Архивированное измерение само по себе не подтверждает приёмку. Для весового режима выберите измерение и подготовьте фотографии. Допуск и актуальность проверит сервер.</p>
  <p role="status">{message}</p>
 </section>;
}
