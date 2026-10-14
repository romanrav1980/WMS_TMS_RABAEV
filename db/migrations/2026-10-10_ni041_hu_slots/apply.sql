@@001_schema.sql
@@002_slot.sql
@@003_commands.sql
@@004_task.sql
@@005_read.sql
@@006_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_SLOT','RRL_STOCK_HU_CMD','RRL_STOCK_HU_TASK','RRL_STOCK_HU_READ') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=8 then raise_application_error(-20808,'HU_SLOT_OBJECTS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-053-hu-slot-task' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Whole HU task frozen SI measurements and current physical slot; single top-place occupied claim; empty-cell bound retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
