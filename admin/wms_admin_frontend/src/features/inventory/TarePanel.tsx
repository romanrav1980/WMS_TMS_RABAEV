import {TareTransferHistory} from "./TareTransferHistory";
import {TareBalanceSummary} from "./TareBalanceSummary";
import "./TareWorkspace.css";
import {useEffect,useState} from "react";
import {TareDamageSource} from "./TareDamageSource";
import {TareLossForm} from "./TareLossForm";
import {TareDamageForm} from "./TareDamageForm";
import {TareDamageCases,type DamageCase,type DamagePick,type DamagePosition} from "./TareDamageCases";
import {TareWriteoffForm} from "./TareWriteoffForm";
import {TareLossCase} from "./TareLossCase";
import {useTare} from "./useTare";
import type {Holder,TareOffer} from "./api";

function AcceptTare({row,confirm,disabled}:{row:TareOffer;confirm:(payload:{offer_operation_id:string;accepted_quantity:string;scan_vehicle:string})=>Promise<void>;disabled:boolean}){
 const [quantity,setQuantity]=useState(""),[vehicle,setVehicle]=useState("");
 return <fieldset disabled={disabled}><p>{row.from_kind} {row.from_id} → {row.to_kind} {row.to_id} · тип {row.pallet_type_id} · {row.condition_code} · предложено {row.quantity} · передал {row.offered_by}</p>
 {row.damage_operation_id&&<p>Источник повреждения: {row.damage_operation_id}</p>}
 <label>Фактически принято тары<input inputMode="numeric" value={quantity} onChange={e=>setQuantity(e.target.value)}/></label><label>Скан машины<input value={vehicle} onChange={e=>setVehicle(e.target.value)}/></label>
 <button title="Подтвердить фактическое количество своей подписью; непринимаемая часть остаётся у отправителя" onClick={()=>void confirm({offer_operation_id:row.operation_id,accepted_quantity:quantity,scan_vehicle:vehicle})}>Получатель принял тару</button></fieldset>;
}
export function TarePanel({tripId,addresses}:{tripId:number;addresses:string[]}){
 const [username,setUsername]=useState(""),[password,setPassword]=useState(""),[owner,setOwner]=useState(""),[type,setType]=useState(""),[condition,setCondition]=useState<"GOOD"|"DAMAGED">("GOOD");
 const [fromKind,setFromKind]=useState<Holder>("VEHICLE"),[toKind,setToKind]=useState<Holder>("STORE"),[fromId,setFromId]=useState(""),[toId,setToId]=useState(addresses[0]||""),[quantity,setQuantity]=useState(""),[vehicle,setVehicle]=useState("");
 const [damageSource,setDamageSource]=useState(""),[preferredDamage,setPreferredDamage]=useState(""),[writeoffPick,setWriteoffPick]=useState("");
 const [cases,setCases]=useState<DamageCase[]>([]),[positions,setPositions]=useState<DamagePosition[]>([]);
 const flow=useTare(tripId,{username,password}),disabled=flow.busy||!!flow.pending||flow.storageBlocked;
 useEffect(()=>{setOwner("");setType("");setFromId("");setToId("");setQuantity("");setVehicle("");setDamageSource("");setPreferredDamage("");setWriteoffPick("");setCases([]);setPositions([]);},[username,tripId]);
 const holderId=(kind:Holder,manual:string)=>kind==="VEHICLE"?String(flow.context?.trip.vehicle_id||""):kind==="WAREHOUSE"?owner:manual;
 const participant=flow.context?.participant;
 const canHold=(kind:Holder,id:string,ware=Number(owner))=>!participant?false:kind==="WAREHOUSE"?(participant.all_warehouses||participant.warehouse_id===ware)&&id===String(ware):kind==="VEHICLE"?participant.trip_driver&&id===String(flow.context?.trip.vehicle_id):participant.stores.includes(id);
 const senderAllowed=canHold(fromKind,holderId(fromKind,fromId));
 function preset(from:Holder,to:Holder){setFromKind(from);setToKind(to);setFromId("");setToId("");setQuantity("");setVehicle("");setDamageSource("");setPreferredDamage("");}
 // Карточка акта выбирает существующую форму: возврат повреждённой тары по участникам или решение о списании.
 function pickDamage(pick:DamagePick){
  setOwner(String(pick.damage.owner_ware_id));setType(String(pick.damage.pallet_type_id));
  if(pick.kind==="writeoff"){setWriteoffPick(pick.damage.operation_id);setTimeout(()=>document.querySelector(".tare-workspace .tare-writeoff")?.scrollIntoView({behavior:"smooth",block:"start"}),50);return;}
  preset(pick.from,pick.to);setCondition("DAMAGED");if(pick.from==="STORE")setFromId(pick.holderId);setPreferredDamage(pick.damage.operation_id);
  setTimeout(()=>document.querySelector(".tare-workspace .tare-offer")?.scrollIntoView({behavior:"smooth",block:"start"}),50);
 }
 const holderOptions=<><option value="WAREHOUSE">Склад</option><option value="VEHICLE">Автомобиль</option><option value="STORE">Магазин</option></>;
 async function offer(){
  const ownerId=Number(owner),typeId=Number(type);
  if(!senderAllowed||participant?.can_offer===false)return;
  if(!Number.isSafeInteger(ownerId)||ownerId<1||!Number.isSafeInteger(typeId)||typeId<1||!holderId(fromKind,fromId)||!holderId(toKind,toId))return;
  await flow.confirm("/offer",{task_id:tripId,owner_ware_id:ownerId,pallet_type_id:typeId,condition,...(condition==="DAMAGED"&&damageSource?{damage_operation_id:damageSource}:{}),from_kind:fromKind,from_id:holderId(fromKind,fromId),to_kind:toKind,to_id:holderId(toKind,toId),quantity,scan_vehicle:vehicle});
 }
 return <section className="driver-st-card tare-workspace"><h2>Оборотная тара</h2><p>Количество поддонов и ролл-кейджей учитывается отдельно от товара. Предложение передачи не меняет баланс; приёмку подтверждает другой участник.</p>
 <fieldset disabled={flow.busy}><label>Учётная запись<input autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)}/></label><label>Пароль<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)}/></label><button disabled={!!flow.pending||!username||!password} onClick={()=>void flow.load()}>Показать передачи этого рейса</button></fieldset>
 {participant&&<p>Доступные подписи: {participant.all_warehouses?"склады-владельцы":participant.warehouse_id?"склад "+participant.warehouse_id:""}{participant.trip_driver?" · водитель данного рейса":""}{participant.stores.length?" · магазины: "+participant.stores.join(", "):""}. Для передачи выберите своего отправителя.</p>}
 {flow.context&&<TareTransferHistory rows={flow.rows} context={flow.context}/>}
 {flow.context&&owner&&<TareBalanceSummary owner={Number(owner)} credentials={{username,password}} revision={flow.revision} disabled={disabled}/>}
 {flow.context&&owner&&<TareDamageCases owner={Number(owner)} credentials={{username,password}} revision={flow.revision} disabled={disabled} onPick={pickDamage} onLoaded={(c,p)=>{setCases(c);setPositions(p);}}/>}
 <div className="tare-presets"><button disabled={disabled||!flow.context} title="Выбрать передачу со склада водителю; скан и подписи вводятся отдельно" onClick={()=>preset("WAREHOUSE","VEHICLE")}>Выдача со склада</button><button disabled={disabled||!flow.context} title="Выбрать передачу от автомобиля магазину" onClick={()=>preset("VEHICLE","STORE")}>Выдача магазину</button><button disabled={disabled||!flow.context} title="Выбрать возврат из магазина водителю" onClick={()=>preset("STORE","VEHICLE")}>Возврат из магазина</button><button disabled={disabled||!flow.context} title="Выбрать возврат от водителя на склад" onClick={()=>preset("VEHICLE","WAREHOUSE")}>Возврат на склад</button></div>
 <fieldset className="tare-offer" key={username+":"+tripId} disabled={disabled||!flow.context}><legend>Отправитель передаёт тару</legend><p>Машина рейса: {flow.context?.trip.vehicle_number}</p><label>Склад-владелец<select aria-label="Склад-владелец" value={owner} onChange={e=>setOwner(e.target.value)}><option value="">Выберите склад</option>{flow.context?.warehouses.map(ware=><option key={ware.id} value={ware.id}>{ware.name}</option>)}</select></label><label>Тип тары<select aria-label="Тип тары" value={type} onChange={e=>setType(e.target.value)}><option value="">Выберите тип тары</option>{flow.context?.types.map(item=><option key={item.pallet_type_id} value={item.pallet_type_id}>{item.pallet_type_name}</option>)}</select></label><label>Состояние<select aria-label="Состояние" value={condition} onChange={e=>{setCondition(e.target.value as "GOOD"|"DAMAGED");setDamageSource("");}}><option value="GOOD">Пригодная</option><option value="DAMAGED">Повреждённая</option></select></label>
 <label>Отправитель<select aria-label="Отправитель" value={fromKind} onChange={e=>setFromKind(e.target.value as Holder)}>{holderOptions}</select></label>{fromKind==="STORE"&&<label>Магазин-отправитель<select aria-label="Магазин-отправитель" value={fromId} onChange={e=>setFromId(e.target.value)}><option value="">Выберите магазин</option>{(flow.context?.stores||addresses).map(addr=><option key={addr}>{addr}</option>)}</select></label>}
 <label>Получатель<select aria-label="Получатель" value={toKind} onChange={e=>setToKind(e.target.value as Holder)}>{holderOptions}</select></label>{toKind==="STORE"&&<label>Магазин-получатель<select aria-label="Магазин-получатель" value={toId} onChange={e=>setToId(e.target.value)}><option value="">Выберите магазин</option>{(flow.context?.stores||addresses).map(addr=><option key={addr}>{addr}</option>)}</select></label>}
 {condition==="DAMAGED"&&owner&&type&&<TareDamageSource owner={Number(owner)} type={Number(type)} holder={fromKind} holderId={holderId(fromKind,fromId)} credentials={{username,password}} value={damageSource} onChange={setDamageSource} preferred={preferredDamage} disabled={disabled||!senderAllowed} revision={flow.revision}/>}
 <datalist id={"tare-addresses-"+tripId}>{addresses.map(address=><option key={address} value={address}/>)}</datalist>
 <label>Количество тары<input inputMode="numeric" value={quantity} onChange={e=>setQuantity(e.target.value)}/></label><label>Скан машины<input value={vehicle} onChange={e=>setVehicle(e.target.value)}/></label><button title="Сохранить предложение передачи; баланс изменится только после подписи получателя" disabled={!senderAllowed||participant?.can_offer===false||!username||!password||!owner||!type||!holderId(fromKind,fromId)||!holderId(toKind,toId)||!quantity||!vehicle} onClick={()=>void offer()}>Предложить передачу</button></fieldset>
 {flow.rows.filter(row=>!row.accept_operation_id&&!row.cancel_operation_id&&canHold(row.to_kind,row.to_id,row.owner_ware_id)&&row.offered_by!==username).map(row=><AcceptTare key={username+":"+row.operation_id} row={row} disabled={disabled||participant?.can_accept===false} confirm={payload=>flow.confirm("/accept",payload)}/>)}
 {flow.context?.permissions?.can_damage===1&&owner&&type&&<TareDamageForm key={username+":"+tripId+":"+owner+":"+type} tripId={tripId} owner={Number(owner)} type={Number(type)} context={flow.context} debts={flow.debts} disabled={disabled} confirm={body=>flow.confirm("/damage",body)} loadDebt={()=>flow.loadDebt(Number(owner))}/>}
 {flow.context&&owner&&(flow.context.permissions?.can_writeoff===1||writeoffPick)&&<TareWriteoffForm owner={Number(owner)} username={username} cases={cases} positions={positions} selected={writeoffPick} canWriteoff={flow.context.permissions?.can_writeoff===1} disabled={disabled} confirm={body=>flow.confirm("/writeoff",body)}/>}
 {flow.context?.permissions?.can_loss_report===1&&owner&&type&&<TareLossForm key={username+":"+tripId+":"+owner+":"+type} tripId={tripId} owner={Number(owner)} type={Number(type)} context={flow.context} credentials={{username,password}} disabled={disabled} confirm={body=>flow.confirm("/loss-report",body)}/>}
 {flow.lastConfirmed?.intent.path==="/loss-report"&&<TareLossCase claim={{operation_id:flow.lastConfirmed.intent.body.operation_id,owner_ware_id:Number(flow.lastConfirmed.intent.body.owner_ware_id),quantity:String(flow.lastConfirmed.intent.body.quantity),decision_reference:String(flow.lastConfirmed.intent.body.decision_reference),custodian_kind:String(flow.lastConfirmed.intent.body.custodian_kind),custodian_id:String(flow.lastConfirmed.intent.body.custodian_id)}}/>}
 <button disabled={disabled||!owner} onClick={()=>void flow.loadDebt(Number(owner))}>Показать долг магазинов по таре</button>
 {flow.debts.filter(row=>row.owner_ware_id===Number(owner)).map((row,index)=><p key={row.store_addr+":"+index}>{row.store_addr} · {row.pallet_type_name} · осталось {row.outstanding_quantity} · {({UNCONFIGURED_LEGACY:"Срок исторической передачи не задан",WAITING_NEXT_DELIVERY:"До следующей подтверждённой поставки",OVERDUE:"Просрочено",OPEN:"Срок не наступил"} as Record<string,string>)[row.debt_state]||row.debt_state}{row.effective_due_at?" · до "+new Date(row.effective_due_at).toLocaleString("ru-RU",{timeZone:row.timezone_region||"UTC"}):""}</p>)}
 {flow.pending&&<button disabled={flow.busy} onClick={()=>void flow.retry()}>Повторить сохранённую операцию</button>}
 {flow.pending?.confirmed&&<button disabled={flow.busy} onClick={flow.restart}>Исправить подтверждённый отказ</button>}<p className={flow.message?"tare-status":undefined} role="status">{flow.message}</p></section>;
}
