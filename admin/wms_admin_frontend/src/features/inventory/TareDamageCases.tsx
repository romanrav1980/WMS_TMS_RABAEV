import {useEffect,useRef,useState} from "react";
import {tareBase,tareRequest} from "./api";
import type {Credentials,Holder} from "./api";

// NI06.3 (C-0015): акты повреждения склада-владельца — исходная выдача, текущий держатель, списанное и следующий шаг.
// Карточка только выбирает существующую форму (возврат или списание); проведение — отдельной кнопкой формы.
export type DamageCase={operation_id:string;owner_ware_id:number;pallet_type_id:number;pallet_type_name:string;custodian_kind:Holder;custodian_id:string;delivery_accept_operation_id:string|null;damaged_quantity:string;written_off_quantity:string;reason_text:string;decision_reference:string;actor:string;created_at:string};
export type DamagePosition={damage_operation_id:string;pallet_type_id:number;custodian_kind:Holder;custodian_id:string;tracked_quantity:string};
export type DamagePick={kind:"return";from:Holder;to:Holder;holderId:string;damage:DamageCase}|{kind:"writeoff";damage:DamageCase;atWarehouse:boolean};
const holders:Record<Holder,string>={WAREHOUSE:"Склад",VEHICLE:"Автомобиль",STORE:"Магазин"};
const big=(v:string|null|undefined)=>{try{return BigInt(v||"0");}catch{return 0n;}};

export function remainingOf(c:DamageCase){return big(c.damaged_quantity)-big(c.written_off_quantity);}
// Следующий шаг определяется текущим подтверждённым держателем повреждённых единиц, а не исходным местом акта.
export function nextStep(c:DamageCase,positions:DamagePosition[]):{label:string;pick:DamagePick|null;hint:string}{
 if(remainingOf(c)<=0n)return{label:"Списано полностью",pick:null,hint:"Решение принято по всем повреждённым единицам акта."};
 const at=positions.filter(p=>p.damage_operation_id===c.operation_id&&big(p.tracked_quantity)>0n);
 const store=at.find(p=>p.custodian_kind==="STORE"),vehicle=at.find(p=>p.custodian_kind==="VEHICLE"),ware=at.find(p=>p.custodian_kind==="WAREHOUSE");
 if(store)return{label:"Вернуть водителю",pick:{kind:"return",from:"STORE",to:"VEHICLE",holderId:store.custodian_id,damage:c},hint:"Магазин передаёт повреждённую тару водителю со ссылкой на этот акт; водитель подтверждает приёмку."};
 if(vehicle)return{label:"Вернуть на склад",pick:{kind:"return",from:"VEHICLE",to:"WAREHOUSE",holderId:vehicle.custodian_id,damage:c},hint:"Водитель передаёт повреждённую тару складу-владельцу; склад подтверждает приёмку."};
 if(ware)return{label:"Решение о списании",pick:{kind:"writeoff",damage:c,atWarehouse:true},hint:"Повреждённая тара на складе-владельце. Списывает независимый сотрудник склада с правом списания."};
 return{label:"Решение о списании",pick:{kind:"writeoff",damage:c,atWarehouse:false},hint:"Текущий держатель не виден вашей учётной записи; решение по месту акта проверит сервер."};
}

export function TareDamageCases({owner,credentials,revision,disabled,onPick,onLoaded}:{owner:number;credentials:Credentials;revision:number;disabled:boolean;onPick:(pick:DamagePick)=>void;onLoaded:(cases:DamageCase[],positions:DamagePosition[])=>void}){
 const scope=tareBase()+"|"+credentials.username+"|"+owner+"|"+revision,current=useRef(scope);current.current=scope;
 const epoch=useRef(0),locked=useRef(false);
 const [cases,setCases]=useState<DamageCase[]|null>(null),[positions,setPositions]=useState<DamagePosition[]>([]),[hasMore,setHasMore]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{epoch.current++;setCases(null);setPositions([]);setMessage("");return()=>{epoch.current++;};},[scope]);
 async function load(){
  if(disabled||locked.current||owner<1)return;const serial=++epoch.current,identity=scope;locked.current=true;setBusy(true);
  try{
   const [list,custody]=await Promise.all([tareRequest<DamageCase[]>("/warehouses/"+owner+"/damage-cases",credentials),tareRequest<{items:DamagePosition[];has_more:boolean}>("/warehouses/"+owner+"/damage-custody",credentials)]);
   if(serial!==epoch.current||identity!==current.current)return;
   setCases(list);setPositions(custody.items);setHasMore(custody.has_more);onLoaded(list,custody.items);
  }catch(e){if(serial===epoch.current&&identity===current.current)setMessage(String(e));}
  finally{locked.current=false;setBusy(false);}
 }
 return <details className="tare-cases" open><summary title="Акты повреждения, текущий держатель повреждённой тары и решение о списании">Повреждённая тара: акты и решения{cases?" · "+cases.length:""}</summary>
  <button type="button" disabled={disabled||busy||owner<1} title="Прочитать акты повреждения и текущее местонахождение повреждённой тары; движение не создаётся" onClick={()=>void load()}>Показать акты повреждения</button>
  <p>До 200 последних актов склада-владельца. Повреждение не меняет общий баланс тары; уменьшает его только решение о списании.</p>
  {cases?.length===0&&<p>Актов повреждения по доступным вам участникам нет.</p>}
  {hasMore&&<p role="status">Показаны первые 200 позиций держателей; отсутствие строки не подтверждает отсутствие тары.</p>}
  {cases?.map(c=>{const step=nextStep(c,positions),at=positions.filter(p=>p.damage_operation_id===c.operation_id&&big(p.tracked_quantity)>0n);
   return <article key={c.operation_id} className={"tare-case"+(remainingOf(c)<=0n?" tare-case-done":"")} aria-label={"Акт "+c.decision_reference}>
    <header><strong>Акт {c.decision_reference}</strong><span className="tare-chip">{step.label}</span></header>
    <dl className="tare-facts">
     <div><dt>Тип тары</dt><dd>{c.pallet_type_name}</dd></div>
     <div><dt>Повреждено</dt><dd>{c.damaged_quantity}</dd></div>
     <div><dt>Списано</dt><dd>{c.written_off_quantity}</dd></div>
     <div><dt>Осталось решить</dt><dd>{remainingOf(c).toString()}</dd></div>
     <div><dt>Выявлено у</dt><dd>{holders[c.custodian_kind]} {c.custodian_id}</dd></div>
     <div><dt>Сейчас у</dt><dd>{at.length?at.map(p=>holders[p.custodian_kind]+" "+p.custodian_id+": "+p.tracked_quantity).join("; "):"—"}</dd></div>
     <div><dt>Зафиксировал</dt><dd>{c.actor}</dd></div>
     <div><dt>Владелец</dt><dd>склад {c.owner_ware_id}</dd></div>
    </dl>
    <details><summary>Основание</summary><p>Акт повреждения: {c.operation_id}</p>{c.delivery_accept_operation_id&&<p>Исходная выдача магазину: {c.delivery_accept_operation_id}</p>}<p>Результат осмотра: {c.reason_text}</p><p>Дата: {new Date(c.created_at).toLocaleString("ru-RU")}</p></details>
    <p className="tare-next">{step.hint}</p>
    {step.pick&&<button type="button" disabled={disabled} title="Выбрать форму ниже; операция проводится отдельной кнопкой формы" onClick={()=>onPick(step.pick!)}>{step.label}</button>}
   </article>;})}
  {message&&<p role="status">{message}</p>}
 </details>;
}
