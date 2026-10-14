from pathlib import Path
import json,re
files={}
p=Path("admin/wms_admin_frontend/src/features/inventory/tareResult.ts");s=p.read_text(encoding="utf-8").replace('tare_balance_changed?:boolean','tare_balance_changed?:boolean;offer_operation_id?:string;quantity?:string')
s=s.replace('if(intent.path==="/accept"&&(', 'if(intent.path==="/accept"&&(r.offer_operation_id!==intent.body.offer_operation_id||r.quantity!==intent.body.accepted_quantity||')
files[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/api.ts");s=p.read_text(encoding="utf-8")
s=s.replace('const detail=data.detail;throw new TareApiError(typeof detail==="string"?detail:detail?.message||"Действие не подтверждено.",','const detail=data.detail;const message=typeof detail==="string"?detail:detail?.message||"Действие не подтверждено.";throw new TareApiError(message==="TARE_RETURN_POLICY_REQUIRED"?"Для магазина не настроен срок возврата тары. Ответственный должен задать правило в разделе сроков возврата; затем исправьте подтверждённый отказ.":message,')
files[str(p)]=s
for name in ["TareDamageForm.tsx","TareLossForm.tsx"]:
 p=Path("admin/wms_admin_frontend/src/features/inventory")/name;s=p.read_text(encoding="utf-8");s=re.sub(r'<label>([^<]+)<select ',r'<label>\1<select aria-label="\1" ',s);files[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TareDamageSource.tsx");s=p.read_text(encoding="utf-8").replace('Акт повреждения<select ','Акт повреждения<select aria-label="Акт повреждения" ');files[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/inventory/TarePanel.tsx");s=p.read_text(encoding="utf-8").replace('flow.debts.map((row,index)', 'flow.debts.filter(row=>row.owner_ware_id===Number(owner)).map((row,index)');files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
