import json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];folder=r/"db/migrations/2026-10-10_ni033_case_scope"
policy=(folder/"000_before_policy.sql").read_text(encoding="utf-8")
policy=policy.replace('  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;',
 '''  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,case when p_action='TRANSFER'then'case_pick_manage'else'case_pick_execute'end);''',1)
policy=policy.replace('  select count(*) into n from RUSERS where ID=target and nvl(DELETED,0)=0;',
 '''  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,case when p_action='TRANSFER'then'case_pick_manage'else'case_pick_execute'end,target);
  select count(*) into n from RUSERS where ID=target and nvl(DELETED,0)=0;''',1)
root=(folder/"000_before_root.sql").read_text(encoding="utf-8")
needle="if g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;"
assert root.count(needle)==2
root=root.replace(needle,needle+"\n  if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;")
(folder/"002_policy_contract.sql").write_text(policy,encoding="utf-8")
(folder/"003_root_contract.sql").write_text(root,encoding="utf-8")
for content,name in [(policy,"002_policy_body.sql"),(root,"003_root_body.sql")]:
 pos=content.lower().index('create or replace package body')
 (folder/name).write_text(content[pos:],encoding="utf-8")
(folder/"apply.sql").write_text('-- MIGRATION_ID:2026-10-10-165-case-current-warehouse\n@@001_access.sql\n@@002_policy_body.sql\n@@003_root_body.sql\n',encoding="utf-8")
(folder/"rollback.sql").write_text('@@000_before_root.sql\n@@000_before_policy.sql\n-- Keep additive access package until no caller references it; no history/data removal.\n',encoding="utf-8")
manifest=r/"db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"
m=json.loads(manifest.read_text(encoding="utf-8-sig"))
m["packages"].insert(m["packages"].index("RRL_CASE_RESOURCE_POLICY"),"RRL_CASE_TASK_ACCESS")
for key,items in m.items():
 if not isinstance(items,list):continue
 for i,value in enumerate(items):
  if value=="../2026-10-09_ni033_pick_release/006_case_policy.sql":items[i:i+1]=["../2026-10-10_ni033_case_scope/001_access.sql","../2026-10-10_ni033_case_scope/002_policy_contract.sql"];break
 for i,value in enumerate(items):
  if value=="../2026-10-10_stock_actor_admission/001_root.sql":items[i]="../2026-10-10_ni033_case_scope/003_root_contract.sql"
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
checkpoint={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob("*.sql")}
(folder/"checkpoint.json").write_text(json.dumps({"migration_id":"2026-10-10-165-case-current-warehouse","files":checkpoint,"scope":"reversible packages/dev RABAEV; saved live sources, no database copy"},indent=2)+"\n",encoding="utf-8")
