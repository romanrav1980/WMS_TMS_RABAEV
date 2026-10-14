@@001_schema.sql
@@002_helper.sql
@@003_task_plan.sql
@@004_task_core.sql
@@005_task_domain.sql
@@006_root.sql
@@007_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_RETURN_PUT','RRL_STOCK_POSTING_API','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_DOMAIN') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'STORE_RETURN_PUTAWAY_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-097-store-return-existing-putaway' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Received ordinary return uses existing warehouse task/planning/transfer/DONE/SYNCED plus immutable placement and ERP outbox; no second task engine',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
