from pathlib import Path
import re,json
base=Path("db/migrations/2026-10-08_stock_posting_core");dest="db/migrations/2026-10-10_ni061_placement/";out={}
def read(name):return re.sub(r"\n\s*\n","\n",(base/name).read_text(encoding="utf-8"))
s=read("433_before120_task_plan.sql");needle="  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='STORE_RETURN' then RRL_STOCK_STORE_RETURN_PUT.plan_task"
assert needle in s;s=s.replace(needle,"  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then RRL_STOCK_INTERWARE_PUT.plan_task(v_task,v_doc.get_string('actor'),v_r,v_domain);end if;\n"+needle,1);out[dest+"003_task_plan.sql"]=s
s=read("434_before120_task_core.sql");needle="  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='STORE_RETURN' then RRL_STOCK_STORE_RETURN_PUT.validate_task"
assert needle in s;s=s.replace(needle,"  if v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then RRL_STOCK_INTERWARE_PUT.validate_task(v_task,p_actor,v_domain.get_object('interwarehouse_placement'));end if;\n"+needle,1)
needle="  elsif v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='STORE_RETURN' then"
assert needle in s;s=s.replace(needle,"  elsif v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then\n   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,'INTERWARE_WHOLE_PLACEMENT_REQUIRED');end if;\n"+needle,1)
needle="case when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY'"
assert needle in s;s=s.replace(needle,"case when v_task.TASK_SOURCE='MANUAL' and v_task.SOURCE_DOC_TYPE='INTERWARE' then 'PUTAWAY' when v_task.TASK_SOURCE='SAP_RECEIPT' then 'PUTAWAY'",1);out[dest+"004_task_core.sql"]=s
s=read("435_before120_task_domain.sql");needle="  if p_task.TASK_SOURCE='MANUAL' and p_task.SOURCE_DOC_TYPE='STORE_RETURN' then"
assert needle in s;s=s.replace(needle,"  if p_task.TASK_SOURCE='MANUAL' and p_task.SOURCE_DOC_TYPE='INTERWARE' then\n   RRL_STOCK_INTERWARE_PUT.complete_task(p_task,p_qty,p_target_uid,p_actor);\n  elsif p_task.TASK_SOURCE='MANUAL' and p_task.SOURCE_DOC_TYPE='STORE_RETURN' then",1);out[dest+"005_task_domain.sql"]=s
s=read("436_before120_root.sql")
s=s.replace("  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command","  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command",1)
s=s.replace("  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command","  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.execute_command(g_request,g_actor,p_result);\n  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command",1)
assert s.count("RRL_STOCK_INTERWARE_PUT")==2;out[dest+"006_root.sql"]=s
out[dest+"007_guards.sql"]="""create or replace trigger RRL_INTERWARE_PUT_GUARD before insert or update or delete on RRL_INTERWARE_PUT_PLAN for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PUT_PLAN_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_PUT_PLAN_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN'and STATE='IN_FLIGHT'and json_value(RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.task_id' returning number)=:new.TASK_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.target_cell')=:new.TARGET_CELL and ACTOR=:new.ACTOR;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PUT_PLAN_RESOLVED_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_RECEIPT',:new.RECEIPT_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PUT_PLAN',op));
end;
/
create or replace trigger RRL_INTERWARE_PLACEMENT_GUARD before insert or update or delete on RRL_INTERWARE_PLACEMENT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PLACEMENT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_PLACEMENT_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='TASK_COMPLETE'and STATE='IN_FLIGHT'and json_value(RESOLVED_PLAN_JSON,'$.domain.task_id' returning number)=:new.TASK_ID and ACTOR=:new.ACTOR;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_TASK_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID where p.TASK_ID=:new.TASK_ID and r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and p.TARGET_CELL=:new.TARGET_CELL and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and r.BASE_QTY=:new.BASE_QTY and r.BASE_UOM=:new.BASE_UOM;
 if n!=1 then raise_application_error(-20863,'INTERWARE_PLACEMENT_ORIGINAL_RECEIPT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_PLACEMENT',to_char(:new.TASK_ID,'TM9')));
end;
/
"""
out[dest+"apply.sql"]="""@@001_schema.sql
@@002_command.sql
@@003_task_plan.sql
@@004_task_core.sql
@@005_task_domain.sql
@@006_root.sql
@@007_guards.sql
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_PUT','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_DOMAIN','RRL_STOCK_POSTING_API','RRL_INTERWARE_PUT_GUARD','RRL_INTERWARE_PLACEMENT_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE120_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-120-interwarehouse-existing-placement-task' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing MANUAL PUTAWAY task for whole original interwarehouse receipt to existing target trip dock; native stock movement',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[dest+"rollback.sql"]="""declare n number;begin select(select count(*)from RRL_INTERWARE_PUT_PLAN)+(select count(*)from RRL_INTERWARE_PLACEMENT)into n from dual;if n!=0 then raise_application_error(-20899,'INTERWARE120_FACTS_FORWARD_CORRECTION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/436_before120_root.sql
@@../2026-10-08_stock_posting_core/433_before120_task_plan.sql
@@../2026-10-08_stock_posting_core/434_before120_task_core.sql
@@../2026-10-08_stock_posting_core/435_before120_task_domain.sql
drop table RRL_INTERWARE_PLACEMENT;
drop table RRL_INTERWARE_PUT_PLAN;
drop package RRL_STOCK_INTERWARE_PUT;
"""
print(json.dumps(out,ensure_ascii=True))
