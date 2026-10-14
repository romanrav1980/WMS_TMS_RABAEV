from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core");d=Path("db/migrations/2026-10-10_stock_actor_admission");out={}
source="../2026-10-10_ni081_task_scope/003_root.sql";text=(base/source).read_text(encoding="utf-8")
needle=" procedure reset_connection is"
assert text.count(needle)==1
text=text.replace(needle,''' procedure assert_actor_active(p_actor varchar2) is v_n number;
 begin
  select count(*)into v_n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if v_n!=1 then raise_application_error(-20882,'STOCK_CURRENT_ACTOR_REQUIRED');end if;
 end;
'''+needle)
needle="  if g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;"
assert text.count(needle)==2
text=text.replace(needle,"  assert_actor_active(p_actor);\n"+needle,1)
needle="  RRL_STOCK_LOCK_API.acquire_resources(v_resources);"
assert text.count(needle)==1
text=text.replace(needle,needle+"\n  assert_actor_active(p_actor);")
out[str(d/"001_root.sql")]=text
start=text.index("create or replace package body RRL_STOCK_POSTING_API as")
out[str(d/"002_body.sql")]=text[start:]
out[str(d/"apply.sql")]="@@002_body.sql\n"
manifest=json.loads((base/"current_runtime_manifest.json").read_text(encoding="utf-8"))
assert source in manifest["components"]
manifest["components"]=["../2026-10-10_stock_actor_admission/001_root.sql"if x==source else x for x in manifest["components"]]
out[str(base/"current_runtime_manifest.json")]=json.dumps(manifest,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
