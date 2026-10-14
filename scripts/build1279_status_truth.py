from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_status.py");s=p.read_text(encoding="utf-8")
s=s.replace("coalesce(lf.ROOT_UID,'CASE:'||to_char(lf.ROOT_CASE_TASK_ID))","coalesce(lf.ROOT_UID,case when lf.ROOT_CASE_TASK_ID is not null then 'CASE:'||to_char(lf.ROOT_CASE_TASK_ID)end)")
s=s.replace("coalesce(ROOT_UID,'CASE:'||to_char(ROOT_CASE_TASK_ID))","coalesce(ROOT_UID,case when ROOT_CASE_TASK_ID is not null then 'CASE:'||to_char(ROOT_CASE_TASK_ID)end)")
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8")
old='el("admission").textContent=data.ready?"Допуск подтверждён":"Ожидает контроля";'
assert old in s;s=s.replace(old,'el("admission").textContent=data.required===false?"Контроль не требуется":data.ready?"Допуск подтверждён":"Ожидает контроля";',1)
old='message.textContent=(data.ready?"Допуск подтверждён. ":"Допуск пока не подтверждён. ")+explain(data.reason)+'
assert old in s;s=s.replace(old,'message.textContent=(data.required===false?"По текущим настройкам контроль не требуется. ":data.ready?"Допуск подтверждён. ":"Допуск пока не подтверждён. ")+explain(data.reason)+',1)
s=s.replace(':" "+explain(data.weight_policy_reason));controls();',':data.required===false?"":" "+explain(data.weight_policy_reason));controls();',1)
point='  const editable=!busy&&!broken&&!pending&&'
assert point in s;s=s.replace(point,'  if(!pending&&snapshot?.required===false)for(const name of["load","scan","weight"])el(name).disabled=true;\n'+point,1)
files[str(p)]=s
print(json.dumps(files))
