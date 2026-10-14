from pathlib import Path
import json
files={};p=Path('wiki-raw/wms_admin_ui_reference/st-deferral.js');t=p.read_text(encoding='utf-8')
t=t.replace("!p.operation_id.startsWith('STDEFER:')","!/^STDEFER:[A-Za-z0-9_.:-]{1,92}$/.test(p.operation_id)")
t=t.replace("!p.st_number.trim()||", "!p.st_number.trim()||p.st_number.length>100||")
t=t.replace("typeof p.source_hash!=='string'||!p.source_hash||", "typeof p.source_hash!=='string'||!/^[a-f0-9]{64}$/.test(p.source_hash)||")
t=t.replace("p.reason.trim().length<8||", "p.reason.trim().length<8||p.reason.length>500||")
t=t.replace("p.reference.trim().length<8)","p.reference.trim().length<8||p.reference.length>500)")
files[str(p)]=t
p=Path('scripts/check800_st_recovery.cjs');files[str(p)]=p.read_text(encoding='utf-8').replace("source_hash:'hash'","source_hash:'a'.repeat(64)")
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation.html');t=p.read_text(encoding='utf-8')
for id,maxlength in [('sdSt',100),('sdReference',500),('sdReason',500)]:
 if 'id="'+id+'" maxlength=' not in t:t=t.replace('id="'+id+'"','id="'+id+'" maxlength="'+str(maxlength)+'"')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
