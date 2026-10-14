import {useState} from "react";
import type {Holder,TareBody,TareDebt,TareContext} from "./api";

export function TareDamageForm({tripId,owner,type,context,debts,disabled,confirm,loadDebt}:{tripId:number;owner:number;type:number;context:TareContext;debts:TareDebt[];disabled:boolean;confirm:(body:Omit<TareBody,"operation_id">)=>Promise<void>;loadDebt:()=>Promise<void>}){
 const [holder,setHolder]=useState<Holder>("STORE"),[loan,setLoan]=useState(""),[quantity,setQuantity]=useState(""),[reason,setReason]=useState(""),[reference,setReference]=useState(""),[scan,setScan]=useState("");
 const loans=debts.filter(row=>row.owner_ware_id===owner&&row.pallet_type_id===type&&row.condition_code==="GOOD");
 async function submit(){
  const body:Omit<TareBody,"operation_id">={owner_ware_id:owner,pallet_type_id:type,custodian_kind:holder,custodian_id:holder==="WAREHOUSE"?String(owner):String(context.trip.vehicle_id),quantity,reason,decision_reference:reference};
  if(holder==="STORE"){const row=loans.find(row=>row.accept_operation_id===loan);if(!row)return;body.custodian_id=row.store_addr;body.delivery_accept_operation_id=row.accept_operation_id;}
  if(holder==="VEHICLE"){body.task_id=tripId;body.scan_vehicle=scan;}
  await confirm(body);
 }
 return <fieldset disabled={disabled}><legend>Осмотр повреждённой тары</legend><label>Место выявления<select aria-label="Место выявления" value={holder} onChange={e=>setHolder(e.target.value as Holder)}><option value="STORE">Магазин</option><option value="VEHICLE">Автомобиль рейса</option><option value="WAREHOUSE">Склад-владелец</option></select></label>
 {holder==="STORE"&&<><button onClick={()=>void loadDebt()}>Показать исходные выдачи</button><label>Выдача магазину<select aria-label="Выдача магазину" value={loan} onChange={e=>setLoan(e.target.value)}><option value="">Выберите выдачу</option>{loans.map(row=><option key={row.claim_key} value={row.accept_operation_id}>{row.store_addr} · осталось {row.outstanding_quantity}</option>)}</select></label></>}
 {holder==="VEHICLE"&&<label>Скан машины<input value={scan} onChange={e=>setScan(e.target.value)}/></label>}
 <label>Повреждено единиц<input inputMode="numeric" value={quantity} onChange={e=>setQuantity(e.target.value)}/></label><label>Результат осмотра<input maxLength={500} value={reason} onChange={e=>setReason(e.target.value)}/></label><label>Номер акта<input maxLength={60} value={reference} onChange={e=>setReference(e.target.value)}/></label>
 <button disabled={!quantity||!reason||!reference||(holder==="STORE"&&!loan)||(holder==="VEHICLE"&&!scan)} onClick={()=>void submit()}>Зафиксировать повреждение</button><p>Тара переводится из пригодной в повреждённую. Общий баланс и исходный срок сохраняются; списание требует отдельного решения.</p></fieldset>;
}
