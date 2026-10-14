from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/features/tare/api.ts")
s=p.read_text(encoding="utf-8-sig")+'''
export type TareContext={trip:{task_id:number;vehicle_id:number;vehicle_number:string};warehouses:{id:number;name:string}[];types:{pallet_type_id:number;pallet_type_name:string;pallet_type_code:string}[];stores:string[]};
'''
p2=Path("admin/wms_admin_frontend/src/features/tare/useTare.ts")
s2=p2.read_text(encoding="utf-8-sig").replace("TareOffer}","TareOffer,TareContext}")
s2=s2.replace('const [pending,','const [context,setContext]=useState<TareContext|null>(null);\n const [pending,')
s2=s2.replace('setRows([]);setMessage("");try','setRows([]);setContext(null);setMessage("");try')
s2=s2.replace('try{const data=await tareRequest<TareOffer[]>("/trips/"+tripId+"/offers",credentials);if(current.current===scope)setRows(data);}','try{const [data,options]=await Promise.all([tareRequest<TareOffer[]>("/trips/"+tripId+"/offers",credentials),tareRequest<TareContext>("/trips/"+tripId+"/context",credentials)]);if(current.current===scope){setRows(data);setContext(options);}}')
s2=s2.replace('return{rows,pending','return{rows,context,pending')
p3=Path("admin/wms_admin_frontend/src/features/tare/TarePanel.tsx")
s3=p3.read_text(encoding="utf-8-sig").replace('import {useState}', 'import {useEffect,useState}')
s3=s3.replace(' const holderOptions=', ''' useEffect(()=>{setOwner("");setType("");setFromId("");setToId("");setQuantity("");setVehicle("");},[username,tripId]);
 const holderId=(kind:Holder,manual:string)=>kind==="VEHICLE"?String(flow.context?.trip.vehicle_id||""):kind==="WAREHOUSE"?owner:manual;
 const holderOptions=''',1)
s3=s3.replace('||!fromId||!toId)return;','||!holderId(fromKind,fromId)||!holderId(toKind,toId))return;')
s3=s3.replace('from_id:fromId,to_kind:toKind,to_id:toId','from_id:holderId(fromKind,fromId),to_kind:toKind,to_id:holderId(toKind,toId)')
s3=s3.replace('<fieldset key={username+":"+tripId} disabled={disabled}>','<fieldset key={username+":"+tripId} disabled={disabled||!flow.context}>')
s3=s3.replace('<label>Склад-владелец<input inputMode="numeric" value={owner} onChange={e=>setOwner(e.target.value)}/></label><label>Тип тары из справочника<input inputMode="numeric" value={type} onChange={e=>setType(e.target.value)}/></label>',
'<label>Склад-владелец<select value={owner} onChange={e=>setOwner(e.target.value)}><option value="">Выберите склад</option>{flow.context?.warehouses.map(ware=><option key={ware.id} value={ware.id}>{ware.name}</option>)}</select></label><label>Тип тары<select value={type} onChange={e=>setType(e.target.value)}><option value="">Выберите тип тары</option>{flow.context?.types.map(item=><option key={item.pallet_type_id} value={item.pallet_type_id}>{item.pallet_type_name}</option>)}</select></label>')
s3=s3.replace('<label>Идентификатор отправителя или адрес магазина<input value={fromId} onChange={e=>setFromId(e.target.value)} list={"tare-addresses-"+tripId}/></label>',
'{fromKind==="STORE"&&<label>Магазин-отправитель<select value={fromId} onChange={e=>setFromId(e.target.value)}><option value="">Выберите магазин</option>{(flow.context?.stores||addresses).map(addr=><option key={addr}>{addr}</option>)}</select></label>}')
s3=s3.replace('<label>Идентификатор получателя или адрес магазина<input value={toId} onChange={e=>setToId(e.target.value)} list={"tare-addresses-"+tripId}/></label>',
'{toKind==="STORE"&&<label>Магазин-получатель<select value={toId} onChange={e=>setToId(e.target.value)}><option value="">Выберите магазин</option>{(flow.context?.stores||addresses).map(addr=><option key={addr}>{addr}</option>)}</select></label>}')
s3=s3.replace('||!fromId||!toId||!quantity','||!holderId(fromKind,fromId)||!holderId(toKind,toId)||!quantity')
s3=s3.replace('<legend>Отправитель передаёт тару</legend>','<legend>Отправитель передаёт тару</legend><p>Машина рейса: {flow.context?.trip.vehicle_number}</p>')
print(json.dumps({str(p):s,str(p2):s2,str(p3):s3},ensure_ascii=True))
