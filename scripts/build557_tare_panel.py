import json
from pathlib import Path
out={}
def patch(p,a,b):
 v=out.get(p,Path(p).read_text(encoding="utf-8"));assert v.count(a)==1,(p,a,v.count(a));out[p]=v.replace(a,b)
p="admin/wms_admin_frontend/src/features/inventory/api.ts"
patch(p,'short_quantity:string|null;vehicle_number:string};','short_quantity:string|null;vehicle_number:string;damage_operation_id?:string|null;cancel_operation_id?:string|null};')
patch(p,'export type TareContext={permissions?:','export type TareContext={participant?:{warehouse_id:number|null;all_warehouses:boolean;trip_driver:boolean;stores:string[];stores_has_more?:boolean;can_offer:boolean;can_accept:boolean};permissions?:')
p="admin/wms_admin_frontend/src/features/inventory/useTare.ts"
patch(p,'const [debts,setDebts]=useState<TareDebt[]>([]);','const [debts,setDebts]=useState<TareDebt[]>([]);\n const [revision,setRevision]=useState(0),[storageBlocked,setStorageBlocked]=useState(false);\n const blockedRef=useRef(false);')
patch(p,'setMessage("");try{const intent=','setMessage("");setStorageBlocked(false);blockedRef.current=false;try{const intent=')
patch(p,'intentRef.current=intent;setPending(intent);}catch{intentRef.current=null;setPending(null);setMessage("Не удалось прочитать сохранённую передачу.");}',
 'if(intent&&(!intent.body||!["/offer","/accept","/damage","/writeoff","/loss-report"].includes(intent.path)||typeof intent.body.operation_id!=="string"||! /^[A-Za-z0-9_.:-]{1,100}$/.test(intent.body.operation_id)||(intent.confirmed!==undefined&&typeof intent.confirmed!=="boolean")))throw new Error("Invalid saved intent");intentRef.current=intent;setPending(intent);}catch{intentRef.current=null;setPending(null);blockedRef.current=true;setStorageBlocked(true);setMessage("Сохранённая операция повреждена. Новые передачи заблокированы; исходная запись сохранена для разбора.");}')
patch(p,'if(locked.current)return;locked.current=true;setBusy(true);','if(locked.current||blockedRef.current)return;locked.current=true;setBusy(true);')
patch(p,'intentRef.current=null;setPending(null);setRows([]);setDebts([]);setMessage(intent.path',
 'intentRef.current=null;setPending(null);setRows([]);setDebts([]);setRevision(v=>v+1);setMessage(intent.path')
patch(p,'if(locked.current||intentRef.current)return;\n  const quan','if(locked.current||intentRef.current||blockedRef.current)return;\n  const quan')
patch(p,'return{rows,debts,loadDebt,context,pending,busy,message,load,confirm,restart,','return{rows,debts,loadDebt,context,pending,busy,message,revision,storageBlocked,load,confirm,restart,')
p="admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx"
patch(p,'import {TareLossForm}', 'import {TareDamageSource} from "./TareDamageSource";\nimport {TareLossForm}')
patch(p,'const flow=useTare(tripId,{username,password}),disabled=flow.busy||!!flow.pending;',
 'const [damageSource,setDamageSource]=useState("");\n const flow=useTare(tripId,{username,password}),disabled=flow.busy||!!flow.pending||flow.storageBlocked;')
patch(p,'setQuantity("");setVehicle("");},[username,tripId]);','setQuantity("");setVehicle("");setDamageSource("");},[username,tripId]);')
patch(p,' const holderOptions=', ''' const participant=flow.context?.participant;
 const canHold=(kind:Holder,id:string,ware=Number(owner))=>!participant?true:kind==="WAREHOUSE"?(participant.all_warehouses||participant.warehouse_id===ware)&&id===String(ware):kind==="VEHICLE"?participant.trip_driver&&id===String(flow.context?.trip.vehicle_id):participant.stores.includes(id);
 const senderAllowed=canHold(fromKind,holderId(fromKind,fromId));
 const holderOptions=''')
patch(p,'condition,from_kind:fromKind,','condition,...(condition==="DAMAGED"&&damageSource?{damage_operation_id:damageSource}:{}),from_kind:fromKind,')
patch(p,'if(!Number.isSafeInteger(ownerId)','if(!senderAllowed||participant?.can_offer===false)return;\n  if(!Number.isSafeInteger(ownerId)')
patch(p,'onChange={e=>setCondition(e.target.value as "GOOD"|"DAMAGED")}', 'onChange={e=>{setCondition(e.target.value as "GOOD"|"DAMAGED");setDamageSource("");}}')
patch(p,' <datalist id=', ' {condition==="DAMAGED"&&owner&&type&&<TareDamageSource owner={Number(owner)} type={Number(type)} holder={fromKind} holderId={holderId(fromKind,fromId)} credentials={{username,password}} value={damageSource} onChange={setDamageSource} disabled={disabled||!senderAllowed} revision={flow.revision}/>}\n <datalist id=')
patch(p,'disabled={!username||!password||!owner||!type||!holderId(fromKind,fromId)','title="Сохранить предложение передачи; баланс изменится только после подписи получателя" disabled={!senderAllowed||participant?.can_offer===false||!username||!password||!owner||!type||!holderId(fromKind,fromId)')
patch(p,'flow.rows.filter(row=>!row.accept_operation_id)','flow.rows.filter(row=>!row.accept_operation_id&&!row.cancel_operation_id&&canHold(row.to_kind,row.to_id,row.owner_ware_id))')
patch(p,'row={row} disabled={disabled}','row={row} disabled={disabled||participant?.can_accept===false}')
patch(p,' <label>Фактически принято тары', ' {row.damage_operation_id&&<p>Источник повреждения: {row.damage_operation_id}</p>}\n <label>Фактически принято тары')
patch(p,'<button onClick={()=>void confirm({offer_operation_id:', '<button title="Подтвердить фактическое количество своей подписью; непринимаемая часть остаётся у отправителя" onClick={()=>void confirm({offer_operation_id:')
print(json.dumps(out))
