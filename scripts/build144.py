from pathlib import Path
import json
d=Path("db/migrations/2026-10-10_ni081_task_scope");out={}
out[str(d/"001_scope.sql")]="""create or replace package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
/
create or replace package body RRL_WAREHOUSE_TASK_ACCESS as
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null) is
  v_from number;v_to number;v_ware number;v_group varchar2(100);
  procedure check_user(p_user varchar2) is
  begin
   if trim(p_user) is null then raise_application_error(-20882,'TASK_ACTIVE_USER_REQUIRED');end if;
   begin
    select WARE_ID,USER_GROUP into v_ware,v_group from RUSERS
     where ID=p_user and nvl(DELETED,0)=0;
   exception when no_data_found then raise_application_error(-20882,'TASK_ACTIVE_USER_REQUIRED');end;
   if upper(trim(v_group))='GLOBAL_ADMIN' then return;end if;
   if v_ware is null or (nvl(v_from,-1)!=v_ware and nvl(v_to,-1)!=v_ware) then
    raise_application_error(-20882,'TASK_USER_WAREHOUSE_FORBIDDEN');end if;
  end;
 begin
  select FROM_WARE_ID,TO_WARE_ID into v_from,v_to from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  check_user(p_actor);
  if p_assignee is not null and p_assignee!=p_actor then check_user(p_assignee);end if;
 end;
 procedure assert_completion(p_request clob,p_actor varchar2) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_meta json_object_t;
  v_task number;v_permission varchar2(100):='warehouse_task_execute';v_task_source varchar2(40);
 begin
  v_source:=v_doc.get_object('source');v_task:=v_source.get_number('task_id');
  assert_scope(v_task,p_actor);
  v_meta:=v_doc.get_object('metadata');
  if v_meta.get_number('document_confirmation')=1 then
   select TASK_SOURCE into v_task_source from RRL_WAREHOUSE_TASK where TASK_ID=v_task;
   if v_task_source!='MES_RAW_SUPPLY' or v_task_source is null then
    raise_application_error(-20882,'MES_DOCUMENT_CONFIRM_FORBIDDEN');end if;
   v_permission:='mes_raw_transfer_confirm';
  end if;
  if RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then
   raise_application_error(-20882,'TASK_CURRENT_EXECUTE_FORBIDDEN');end if;
 end;
end;
/
"""
base=Path("db/migrations/2026-10-08_stock_posting_core")
manifest=json.loads((base/"current_runtime_manifest.json").read_text(encoding="utf-8"))
policy="../2026-10-09_ni033_pick_release/007_task_policy.sql"
root="../2026-10-10_ni063_warehouse_tare_loss/005_root.sql"
assert policy in manifest["components"] and root in manifest["components"]
text=(base/policy).read_text(encoding="utf-8")
needle="  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;"
assert text.count(needle)==1
out[str(d/"002_policy.sql")]=text.replace(needle,needle+"\n  RRL_WAREHOUSE_TASK_ACCESS.assert_scope(p_task,v_actor,v_target);")
text=(base/root).read_text(encoding="utf-8")
needle="  -- Immutable committed replay is considered before any mutable article/cell/UOM validation."
assert text.count(needle)==1
call="  if g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE') then RRL_WAREHOUSE_TASK_ACCESS.assert_completion(p_request,p_actor);end if;\n"
text=text.replace(needle,call+needle)
needle="  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);"
assert text.count(needle)==1
text=text.replace(needle,call+needle)
out[str(d/"003_root.sql")]=text
out[str(d/"apply.sql")]="@@001_scope.sql\n@@002_policy.sql\n@@003_root.sql\n"
idx=manifest["components"].index(policy);manifest["components"].insert(idx,"../2026-10-10_ni081_task_scope/001_scope.sql")
manifest["components"]=[("../2026-10-10_ni081_task_scope/002_policy.sql" if x==policy else "../2026-10-10_ni081_task_scope/003_root.sql" if x==root else x)for x in manifest["components"]]
manifest["packages"].append("RRL_WAREHOUSE_TASK_ACCESS")
out[str(base/"current_runtime_manifest.json")]=json.dumps(manifest,indent=2)+"\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py");text=p.read_text(encoding="utf-8")
needle="            getattr(service, action)(task_id, request)"
assert text.count(needle)==1
text=text.replace(needle,"""            cursor.execute(
                "begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor,:assignee);end;",
                {"task": task_id, "actor": request.updated_by,
                 "assignee": request.assigned_to if action == "assign_task" else None},
            )
"""+needle)
text=text.replace('        raise HTTPException(code, detail={"code": exc.code,','        if exc.oracle_code == 20882:\n            code = 403\n        raise HTTPException(code, detail={"code": exc.code,')
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
