from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/inventory/api.ts");s=p.read_text(encoding="utf-8-sig")
s=s.replace('path:"/offer"|"/accept";','path:"/offer"|"/accept"|"/damage"|"/writeoff";')
s=s.replace('export type TareContext={trip:', 'export type TareContext={permissions?:{can_damage:number;can_writeoff:number};trip:')
s=s.replace('export type TareDebt={store_addr:', 'export type TareDebt={owner_ware_id:number;pallet_type_id:number;condition_code:string;claim_key:string;accept_operation_id:string;store_addr:')
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/useTare.ts");s=p.read_text(encoding="utf-8-sig")
s=s.replace('const quantity=payload.quantity??payload.accepted_quantity;','const quantity=payload.quantity??payload.accepted_quantity;')
s=s.replace('||!payload.scan_vehicle){','||(path!=="/damage"&&path!=="/writeoff"&&!payload.scan_vehicle)){')
s=s.replace('if(typeof quantity!==','if((path==="/damage"||path==="/writeoff")&&(!payload.reason||!payload.decision_reference)){setMessage("Укажите причину и номер акта или решения.");return;}\n  if(typeof quantity!==',1)
s=s.replace('if(current.current===scope){intentRef.current=null;setPending(null);setRows([]);setMessage(result.status===','if(current.current===scope){intentRef.current=null;setPending(null);setRows([]);setDebts([]);setMessage(intent.path==="/damage"?"Повреждение зафиксировано; общий баланс тары сохранён.":result.status===')
out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx");s=p.read_text(encoding="utf-8-sig").replace('import {useTare}', 'import {TareDamageForm} from "./TareDamageForm";\nimport {useTare}')
s=s.replace(' <button disabled={disabled||!owner}', ''' {flow.context?.permissions?.can_damage===1&&owner&&type&&<TareDamageForm key={username+":"+tripId+":"+owner+":"+type} tripId={tripId} owner={Number(owner)} type={Number(type)} context={flow.context} debts={flow.debts} disabled={disabled} confirm={body=>flow.confirm("/damage",body)} loadDebt={()=>flow.loadDebt(Number(owner))}/>}
 <button disabled={disabled||!owner}''',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace('return {"customers":customers,','permissions=self.gateway.fetch_all("select RRL_HAS_WRIGHT(:actor,\'tare_damage\') CAN_DAMAGE,RRL_HAS_WRIGHT(:actor,\'tare_writeoff\') CAN_WRITEOFF from dual",{"actor":actor})[0]\n        return {"permissions":permissions,"customers":customers,')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
