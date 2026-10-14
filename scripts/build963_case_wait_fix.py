from pathlib import Path
import json,re,hashlib
d="db/migrations/2026-10-13_ni072_case_wait/";p=d+"002_case_wait.sql";body=Path(p).read_text(encoding="utf-8")
for name in("sync_key","sync_id"):
 body=re.sub(r"(?<!['\\w])"+name+r"(?!['\\w])","v_"+name,body)
files={p:body,d+"fix963.sql":"@@002_case_wait.sql\n@@008_compile.sql\n"}
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["correction963"]="Rename sync local variables to avoid Oracle column tautology in lookup;962 failed before movement, retained plan.";v["sha256"].update({p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- 2026-10-13 checkpoint963:961 registerCASEtask1107/rollback+replay succeeded;962 move compilation refused01422 beforequantity due sync_key shadowing, corrected localv_sync_key/v_sync_id; same originalCASE retained, no factoryrerun.\n"
p="wiki/index.md";files[p]="- [CASE ожидание963](database/retailcase_ni072_case_wait_20261013.md): immutable plan registered; sync lookup shadowing correction before movement.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
