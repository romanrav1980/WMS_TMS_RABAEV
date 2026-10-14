from pathlib import Path
import json
files={}
p=Path("admin/wms_admin_frontend/src/features/inventory/api.ts");s=p.read_text(encoding="utf-8").replace('cancel_operation_id?:string|null','accepted_by?:string|null;cancel_reason?:string|null;cancel_operation_id?:string|null');files[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/useTare.ts");s=p.read_text(encoding="utf-8")
s='import {tareResult} from "./tareResult";\n'+s
s=s.replace('useEffect(()=>{setRows([]);','useEffect(()=>{current.current=key;setRows([]);')
s=s.replace('async function load(){','async function readContext(scope:string){\n const [data,options]=await Promise.all([tareRequest<TareOffer[]>("/trips/"+tripId+"/offers",credentials),tareRequest<TareContext>("/trips/"+tripId+"/context",credentials)]);if(current.current===scope){setRows(data);setContext(options);}\n }\n async function load(){')
old='const [data,options]=await Promise.all([tareRequest<TareOffer[]>("/trips/"+tripId+"/offers",credentials),tareRequest<TareContext>("/trips/"+tripId+"/context",credentials)]);if(current.current===scope){setRows(data);setContext(options);}'
# Only replace second occurrence in load, retaining helper
pos=s.index('async function load(){');s=s[:pos]+s[pos:].replace(old,'await readContext(scope);',1)
s=s.replace('const result=await tareRequest<{status:string;destination_quantity?:string;short_quantity?:string}>(intent.path,credentials,intent.body);localStorage.removeItem(scope);','const result=tareResult(await tareRequest<unknown>(intent.path,credentials,intent.body),intent);localStorage.removeItem(scope);')
s=s.replace('tara remains', 'tara remains')
s=s.replace('До приёмки другого участника тара остаётся у отправителя.");}}','До приёмки другого участника тара остаётся у отправителя.");\n    try{await readContext(scope);}catch{if(current.current===scope){setContext(null);setMessage("Операция подтверждена. Не удалось обновить список — нажмите «Показать передачи этого рейса».");}}}}')
s=s.replace('setMessage("Обновите передачи и исправьте данные.");','setContext(null);setMessage("Обновите передачи и исправьте данные.");')
files[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx");s=p.read_text(encoding="utf-8")
s='import {TareTransferHistory} from "./TareTransferHistory";\nimport {TareBalanceSummary} from "./TareBalanceSummary";\nimport "./TareWorkspace.css";\n'+s
s=s.replace('return <section className="driver-st-card">','return <section className="driver-st-card tare-workspace">')
s=s.replace('const senderAllowed=', 'const senderAllowed=') # preserve native permission interpretation
s=s.replace(' const holderOptions=', ''' function preset(from:Holder,to:Holder){setFromKind(from);setToKind(to);setFromId("");setToId("");setQuantity("");setVehicle("");setDamageSource("");}
 const holderOptions=''')
s=s.replace('<fieldset key={username+":"+tripId}', '''{flow.context&&<TareTransferHistory rows={flow.rows} context={flow.context}/>}
 {flow.context&&owner&&<TareBalanceSummary owner={Number(owner)} credentials={{username,password}} revision={flow.revision} disabled={disabled}/>}
 <div className="tare-presets"><button disabled={disabled||!flow.context} title="Выбрать передачу со склада водителю; скан и подписи вводятся отдельно" onClick={()=>preset("WAREHOUSE","VEHICLE")}>Выдача со склада</button><button disabled={disabled||!flow.context} title="Выбрать передачу от автомобиля магазину" onClick={()=>preset("VEHICLE","STORE")}>Выдача магазину</button><button disabled={disabled||!flow.context} title="Выбрать возврат из магазина водителю" onClick={()=>preset("STORE","VEHICLE")}>Возврат из магазина</button><button disabled={disabled||!flow.context} title="Выбрать возврат от водителя на склад" onClick={()=>preset("VEHICLE","WAREHOUSE")}>Возврат на склад</button></div>
 <fieldset key={username+":"+tripId}''')
s=s.replace('const canHold=(kind:Holder,id:string,ware=Number(owner))=>!participant?true:', 'const canHold=(kind:Holder,id:string,ware=Number(owner))=>!participant?false:')
s=s.replace('<p role="status">{flow.message}</p>','<p className={flow.message?"tare-status":undefined} role="status">{flow.message}</p>')
s=s.replace('row.to_kind,row.to_id,row.owner_ware_id)).map','row.to_kind,row.to_id,row.owner_ware_id)&&row.offered_by!==username).map')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
