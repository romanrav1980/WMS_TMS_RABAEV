import type {TareOffer,TareContext,Holder} from "./api";
const holders:Record<Holder,string>={WAREHOUSE:"Склад",VEHICLE:"Автомобиль",STORE:"Магазин"};
export function TareTransferHistory({rows,context}:{rows:TareOffer[];context:TareContext}){
 const name=(kind:Holder,id:string)=>kind==="WAREHOUSE"?context.warehouses.find(w=>String(w.id)===id)?.name||id:kind==="VEHICLE"&&String(context.trip.vehicle_id)===id?context.trip.vehicle_number:id;
 const waiting=rows.filter(r=>!r.accept_operation_id&&!r.cancel_operation_id).length;
 return <details className="tare-history" open><summary title="Показать сохранённые предложения и подписи получателей">История передач · {rows.length} · ожидают подписи {waiting}</summary>
 <p>До 100 последних передач этого рейса. Предложение само по себе не меняет баланс.</p>
 {!rows.length&&<p>Передач этого рейса пока нет.</p>}
 {rows.map(row=><article className="tare-transfer" key={row.operation_id}>
 <strong>{row.cancel_operation_id?"Отменено":row.accept_operation_id?"Приёмка подтверждена":"Ожидает получателя"}</strong>
 <p>{holders[row.from_kind]} {name(row.from_kind,row.from_id)} → {holders[row.to_kind]} {name(row.to_kind,row.to_id)}</p>
 <p>{context.types.find(t=>t.pallet_type_id===row.pallet_type_id)?.pallet_type_name||"Тип "+row.pallet_type_id} · {row.condition_code==="GOOD"?"Пригодная":"Повреждённая"} · предложено {row.quantity}</p>
 {row.accept_operation_id&&<p>Принято: {row.accepted_quantity} · осталось у отправителя: {row.short_quantity}</p>}
 <details><summary title="Показать идентификаторы и участников передачи">Основание и подписи</summary><p>Предложение: {row.operation_id}</p><p>Отправитель: {row.offered_by}</p>
 {row.accept_operation_id&&<p>Приёмка: {row.accept_operation_id} · получатель: {row.accepted_by||"по журналу"}</p>}
 {row.damage_operation_id&&<p>Акт повреждения: {row.damage_operation_id}</p>}
 {row.cancel_operation_id&&<p>Отмена: {row.cancel_operation_id} · {row.cancel_reason}</p>}</details>
 </article>)}</details>;
}
