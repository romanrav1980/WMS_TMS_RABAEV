raise SystemExit('Historical builder retired; use canonical migration apply.sql and 003_command.sql')
# HISTORICAL BUILDER: do not rerun; corrected canonical SQL is 003_command.sql.
from pathlib import Path
import json
d=Path("db/migrations/2026-10-14_ni033_pick_create_idempotency")
s=(d/"001_api.sql").read_text(encoding="utf-8")
s=s[s.index("create or replace package RRL_PICK_PLAN_CREATE_API"):]
s=s[:s.index("create or replace trigger")]
s=s.replace(" procedure assert_write(p_operation varchar2);"," procedure assert_write(p_operation varchar2);\n function current_operation return varchar2;\n function cached_plan return number;")
s=s.replace("g_operation varchar2(100);g_tx varchar2(100);","g_operation varchar2(100);g_tx varchar2(100);g_hash varchar2(64);g_actor varchar2(100);g_ware number;\n function current_operation return varchar2 is begin return g_operation;end;\n function cached_plan return number is v RRL_PICK_PLAN_CREATE_OP%rowtype;begin\n if g_operation is null then return null;end if;\n begin select *into v from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=g_operation;exception when no_data_found then return null;end;\n if v.REQUEST_HASH!=g_hash or v.ACTOR!=g_actor or v.WARE_ID!=g_ware then raise_application_error(-20886,'PICK_CREATE_OPERATION_CONTENT_CONFLICT');end if;\n if v.PICK_PLAN_ID is null then raise_application_error(-20886,'PICK_CREATE_SAVED_RESULT_REQUIRED');end if;return v.PICK_PLAN_ID;end;")
a=s.index("  inserted:=false;")
b=s.index("  g_operation:=null;g_tx:=null;\n  return plan_no;",a)
s=s[:a]+"""  select count(*)into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='ACTIVE';
  if n!=1 then raise_application_error(-20860,'PICK_CREATE_ACTIVE_REQUIRED');end if;
  inserted:=false;
  g_operation:=p_operation;g_hash:=request_hash;g_actor:=p_actor;g_ware:=ware_no;
  plan_no:=RRL_PICKING_API.create_plan(p_order,strategy_value,p_actor);inserted:=true;
  select count(*)into n from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=p_operation;
  if n=0 then
   g_tx:=dbms_transaction.local_transaction_id(false);
   insert into RRL_PICK_PLAN_CREATE_OP(OPERATION_ID,REQUEST_HASH,ACTOR,CUSTOMER_ORDER_ID,WARE_ID,PLAN_STRATEGY,PICK_PLAN_ID)
    values(p_operation,request_hash,p_actor,p_order,ware_no,strategy_value,plan_no);
  end if;
"""+s[b:]
s=s.replace("  inserted:=false;","  inserted:=false;inserted:=true;")
a=(d/"000_before_rrl_pick_plan_admission.sql").read_text(encoding="utf-8")
needle="  RRL_STOCK_LOCK_API.begin_plan;"
assert a.count(needle)==1
a=a.replace(needle,"  if RRL_PICK_PLAN_CREATE_API.current_operation is not null then RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',RRL_PICK_PLAN_CREATE_API.current_operation);end if;\n"+needle)
p=(d/"000_before_rrl_picking_api.sql").read_text(encoding="utf-8")
needle="    v_strategy := upper(nvl(p_plan_strategy, 'FEFO'));"
assert p.count(needle)==1
p=p.replace(needle,"    if v_fenced then v_bound_plan:=RRL_PICK_PLAN_CREATE_API.cached_plan;\n     if v_bound_plan is not null then RRL_PICK_PLAN_ADMISSION.end_plan;return v_bound_plan;end if;end if;\n"+needle)
files={str(d/"003_command.sql"):s,str(d/"004_admission.sql"):a,str(d/"005_picking.sql"):p,str(d/"correction_apply.sql"):"@@003_command.sql\n@@004_admission.sql\n@@005_picking.sql\n"}
print(json.dumps(files,ensure_ascii=True))
