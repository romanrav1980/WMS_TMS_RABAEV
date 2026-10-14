import {useEffect,useRef,useState} from "react";
import {tareBase,tareRequest} from "./api";
import type {Credentials,Holder} from "./api";
type Position={damage_operation_id:string;pallet_type_id:number;custodian_kind:Holder;custodian_id:string;tracked_quantity:string;damage_actor:string;damage_reference:string};
type Page={warehouse_id:number;items:Position[];has_more:boolean};
export function TareDamageSource({owner,type,holder,holderId,credentials,value,onChange,disabled,revision,preferred=""}:{owner:number;type:number;holder:Holder;holderId:string;credentials:Credentials;value:string;onChange:(value:string)=>void;disabled:boolean;revision:number;preferred?:string}){
 const scope=tareBase()+":"+credentials.username+":"+owner+":"+type+":"+holder+":"+holderId;
 const epoch=useRef(0),running=useRef(false);
 const [rows,setRows]=useState<Position[]>([]),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{epoch.current++;setRows([]);setMessage("");setBusy(false);onChange("");return()=>{epoch.current++;};},[scope,revision,onChange]);
 async function load(){
  if(running.current||disabled)return;running.current=true;const request=++epoch.current;setBusy(true);
  try{
   const page=await tareRequest<Page>("/warehouses/"+owner+"/damage-custody",credentials);
   if(request===epoch.current){
    const found=page.items.filter(r=>r.pallet_type_id===type&&r.custodian_kind===holder&&r.custodian_id===holderId);setRows(found);
    if(preferred&&found.some(r=>r.damage_operation_id===preferred))onChange(preferred);
    setMessage(page.has_more?"Показаны первые 200 позиций. Отсутствие записи не подтверждает отсутствие тары.":"Показано подтверждённое происхождение; доступность повторно проверяется при приёмке.");
   }
  }catch(e){if(request===epoch.current)setMessage(String(e));}
  finally{running.current=false;if(request===epoch.current)setBusy(false);}
 }
 // Акт, выбранный в карточке повреждения, подгружается и выбирается сразу; отправка остаётся отдельной кнопкой.
 // eslint-disable-next-line react-hooks/exhaustive-deps
 useEffect(()=>{if(preferred&&holderId&&!disabled)void load();},[preferred,scope]);
 return <fieldset disabled={disabled}><legend>Источник повреждённой тары</legend>
  <button type="button" title="Получить акты повреждения с текущим подтверждённым количеством у выбранного отправителя" disabled={busy||owner<1||type<1||!holderId} onClick={()=>void load()}>Показать исходные акты</button>
  <label title="Сохранить исходное повреждение в предложении передачи">Акт повреждения<select aria-label="Акт повреждения" title="Выберите акт, количество которого сейчас подтверждено у отправителя" value={value} onChange={e=>onChange(e.target.value)}>
   <option value="">Без отслеживаемого исходника — только историческая тара</option>
   {rows.map(r=><option key={r.damage_operation_id} value={r.damage_operation_id}>{r.damage_reference} · {r.damage_actor} · количество {r.tracked_quantity} · {r.damage_operation_id}</option>)}
  </select></label>
  <p>Для новых актов повреждения исходник обязателен. Передача сохраняет связь с актом до возврата и списания.</p>
  {message&&<p role="status">{message}</p>}
 </fieldset>;
}
