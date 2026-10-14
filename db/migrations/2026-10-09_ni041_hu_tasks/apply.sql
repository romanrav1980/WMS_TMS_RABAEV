@@001_schema.sql
@@002_read.sql
@@003_commands.sql
@@004_task_plan.sql
@@005_task_commands.sql
@@006_posting.sql
@@007_task_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_READ','RRL_STOCK_HU_CMD','RRL_STOCK_HU_TASK','RRL_STOCK_POSTING_API','RRL_STOCK_TASK_PLAN') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'HU_TASK_OBJECTS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-052-hu-warehouse-task' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'HU plan reuses MANUAL/PUTAWAY, existing assign/start/resource policy, root whole completion, per-leaf stock move and existing sync key; one physical HU fact',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
