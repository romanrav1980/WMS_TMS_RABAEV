from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/inventory/api.ts");s=p.read_text(encoding="utf-8-sig").replace('"/writeoff";body','"/writeoff"|"/loss-report";body',1).replace("can_writeoff:number","can_writeoff:number;can_loss_report:number",1);out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/useTare.ts");s=p.read_text(encoding="utf-8-sig").replace('path==="/damage"||path==="/writeoff"','path==="/damage"||path==="/writeoff"||path==="/loss-report"',1).replace('path!=="/damage"&&path!=="/writeoff"','path!=="/damage"&&path!=="/writeoff"&&path!=="/loss-report"',1)
s=s.replace('setMessage(intent.path==="/damage"?','setMessage(intent.path==="/loss-report"?"Недостача зарегистрирована. Спорная тара недоступна до независимого решения.":intent.path==="/damage"?',1);out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx");s=p.read_text(encoding="utf-8-sig").replace('import {TareDamageForm}','import {TareLossForm} from "./TareLossForm";\nimport {TareDamageForm}',1)
needle=' <button disabled={disabled||!owner}'
s=s.replace(needle,' {flow.context?.permissions?.can_loss_report===1&&owner&&type&&<TareLossForm key={username+":"+tripId+":"+owner+":"+type} tripId={tripId} owner={Number(owner)} type={Number(type)} context={flow.context} credentials={{username,password}} disabled={disabled} confirm={body=>flow.confirm("/loss-report",body)}/>}\n'+needle,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");s=p.read_text(encoding="utf-8-sig").replace("CAN_WRITEOFF from dual","CAN_WRITEOFF,RRL_HAS_WRIGHT(:actor,'tare_loss_report') CAN_LOSS_REPORT from dual",1);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/tare-loss.js");s=p.read_text(encoding="utf-8-sig").replace('r.pallet_type_name+" · "+r.condition_code+" · "+r.quantity','r.pallet_type_name+" · "+r.custodian_kind+" "+r.custodian_id+" · "+r.condition_code+" · "+r.quantity',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
