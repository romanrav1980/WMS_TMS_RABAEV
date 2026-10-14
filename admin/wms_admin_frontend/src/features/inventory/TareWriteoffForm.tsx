import {useEffect,useState} from "react";
import type {TareBody} from "./api";
import {remainingOf,type DamageCase,type DamagePosition} from "./TareDamageCases";

// NI06.3 (C-0015): решение о списании повреждённой тары по существующей команде /writeoff.
// Сервер требует право tare_writeoff и другого сотрудника, чем автор акта; на складе-владельце — сотрудника этого склада.
export function TareWriteoffForm({owner,username,cases,positions,selected,canWriteoff,disabled,confirm}:{owner:number;username:string;cases:DamageCase[];positions:DamagePosition[];selected:string;canWriteoff:boolean;disabled:boolean;confirm:(body:Omit<TareBody,"operation_id">)=>Promise<void>}){
 const [damage,setDamage]=useState(selected),[quantity,setQuantity]=useState(""),[reason,setReason]=useState(""),[reference,setReference]=useState("");
 useEffect(()=>{setDamage(selected);setQuantity("");},[selected]);
 const open=cases.filter(c=>c.owner_ware_id===owner&&remainingOf(c)>0n);
 const row=open.find(c=>c.operation_id===damage);
 const atWarehouse=!!row&&positions.some(p=>p.damage_operation_id===row.operation_id&&p.custodian_kind==="WAREHOUSE"&&p.custodian_id===String(owner)&&BigInt(p.tracked_quantity)>0n);
 const sameActor=!!row&&row.actor===username;
 const qty=/^[0-9]{1,18}$/.test(quantity)?BigInt(quantity):0n;
 const tooMany=!!row&&qty>remainingOf(row);
 const blocked=!canWriteoff?"Нужно право списания тары (tare_writeoff).":sameActor?"Акт зафиксировали вы — решение о списании принимает другой сотрудник.":"";
 async function submit(){
  if(!row||blocked||tooMany||qty<=0n)return;
  const body:Omit<TareBody,"operation_id">={damage_operation_id:row.operation_id,quantity,reason,decision_reference:reference};
  if(atWarehouse)body.writeoff_warehouse_id=owner;
  await confirm(body);
 }
 return <fieldset className="tare-writeoff" disabled={disabled}><legend>Решение о списании повреждённой тары</legend>
  <label>Акт повреждения<select aria-label="Акт повреждения для списания" value={damage} onChange={e=>{setDamage(e.target.value);setQuantity("");}}><option value="">Выберите акт</option>{open.map(c=><option key={c.operation_id} value={c.operation_id}>{c.decision_reference} · {c.pallet_type_name} · осталось решить {remainingOf(c).toString()} · {c.actor}</option>)}</select></label>
  {row&&<p className="tare-next">{atWarehouse?"Тара возвращена на склад-владелец "+owner+": списание со склада, решает сотрудник этого склада.":"Тара не на складе-владельце: списание у держателя по месту акта ("+row.custodian_kind+" "+row.custodian_id+")."} Автор акта: {row.actor}. Осталось решить: {remainingOf(row).toString()}.</p>}
  <label>Списать единиц<input inputMode="numeric" value={quantity} aria-invalid={tooMany} onChange={e=>setQuantity(e.target.value)}/></label>
  {tooMany&&<p role="alert">Больше, чем осталось решить по акту.</p>}
  <label>Основание решения<input maxLength={500} value={reason} onChange={e=>setReason(e.target.value)}/></label>
  <label>Номер решения<input maxLength={60} value={reference} onChange={e=>setReference(e.target.value)}/></label>
  {blocked&&<p role="status">{blocked}</p>}
  <button title="Списать повреждённую тару; общий баланс уменьшится, товар не затрагивается" disabled={!row||!!blocked||tooMany||qty<=0n||!reason||!reference} onClick={()=>void submit()}>Списать повреждённую тару</button>
  <p>Решение необратимо уменьшает учтённый баланс тары. Повреждение без решения остаётся на учёте как повреждённое.</p>
 </fieldset>;
}
