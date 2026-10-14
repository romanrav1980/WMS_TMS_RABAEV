from pathlib import Path
import json,hashlib
f={};folder="db/migrations/2026-10-13_ni072_shared_wait_target/"
def read(n,k):return Path("tmp/1085_"+n+"_"+k+".sql").read_text(encoding="utf-8")
spec=read("rrl_stock_hu_cmd","package");body=read("rrl_stock_hu_cmd","package_body");task=read("rrl_stock_hu_task","package_body")
for p,t in(("006_hu_spec.sql",spec),("007_hu_boundary.sql",body)):
 old="p_allow_slotted boolean default false)";assert old in t
 t=t.replace(old,"p_allow_slotted boolean default false,p_defer_wait_planning boolean default false)",1)
 if p=="007_hu_boundary.sql":
  old="v_wait_shared:=RRL_ST_DEFER_HU_WAIT.shared_wait_target(p_request,v_ignore_task,v_target,v_target_ware);"
  assert old in t
  t=t.replace(old,"if p_defer_wait_planning or v_ignore_task is not null then "+old+"end if;",1)
 f[folder+p]=t
old="RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain);"
assert task.count(old)==2
task=task.replace(old,"RRL_STOCK_HU_CMD.compile_command(pr,p_operation,p_policies,p_resources,p_domain,p_defer_wait_planning=>true);",1)
f[folder+"008_hu_task.sql"]=task
f[folder+"fix1085.sql"]="@@006_hu_spec.sql\n@@007_hu_boundary.sql\n@@008_hu_task.sql\n@@005_compile.sql\n"
for n,k in(("rrl_stock_hu_cmd","package"),("rrl_stock_hu_task","package_body")):f[folder+"000_before_"+n+"_"+k+".sql"]=read(n,k)
f[folder+"apply.sql"]=Path(folder+"apply.sql").read_text(encoding="utf-8")+"@@fix1085.sql\n"
rollback=Path(folder+"rollback.sql").read_text(encoding="utf-8")
f[folder+"rollback.sql"]="@@000_before_rrl_stock_hu_cmd_package.sql\n@@000_before_rrl_stock_hu_task_package_body.sql\n"+rollback
p="wiki/database/retailcase_ni072_shared_wait_target_20261013.md"
f[p]=Path(p).read_text(encoding="utf-8")+"\n1085: явный параметр только у доверенного HU_TASK compile(planning), либо существующий physical WAIT task. Generic HU_MOVE не получает разрешение общей зоны из произвольного metadata/defer ID. Caller ACL и обычное API неизменны. FreshHU spec/task capture перед применением; actual1080 уже DONE/P20H20, отрицательный generic-call ещё ожидает.\n"
f["wiki/index.md"]="- [Planning boundary1085](database/retailcase_ni072_shared_wait_target_20261013.md): native private planning flag or registered physical WAIT task, no generic metadata bypass.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1085: shared target admission bound to native HU_TASK planning flag/actual WAIT task; generic metadata cannot request bypass. Original1080 actual mixed tasks DONE/P20H20.\n"
print(json.dumps(f,ensure_ascii=True))
