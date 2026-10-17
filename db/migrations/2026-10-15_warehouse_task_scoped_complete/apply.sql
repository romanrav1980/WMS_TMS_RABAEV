-- MIGRATION_ID: 2026-10-15-warehouse-task-scoped-complete
@@task_plan_spec.sql
@@access_spec.sql
@@access_body.sql
@@resource_policy.sql
@@task_core.sql
@@task_plan.sql
@@posting.sql
alter package RRL_STOCK_HU_TASK compile body;
alter package RRL_ST_DEFER_CASE_WAIT compile body;
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WAREHOUSE_TASK_ACCESS','RRL_TASK_RESOURCE_POLICY','RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_PLAN','RRL_STOCK_POSTING_API');
 if n!=0 then raise_application_error(-20886,'TASK_SCOPED_COMPLETE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'TASK_SCOPED_COMPLETE_GLOBAL_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-task-scoped-complete' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped assigned ordinary STOCK task canonical completion; legacy assignment/session policies retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
