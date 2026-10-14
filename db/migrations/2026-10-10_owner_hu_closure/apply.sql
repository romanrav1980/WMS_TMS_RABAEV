@@001_need.sql
@@002_finish.sql
@@003_hu_read.sql
@@004_hu_commands.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_NEED','RRL_STOCK_WAVE_FINISH_CMD','RRL_STOCK_HU_READ','RRL_STOCK_HU_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=8 then raise_application_error(-20808,'OWNER_HU_CLOSURE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-056-owner-hu-closure' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Target HARD same customer owner; bounded actual-wave fulfillment rows; HU unit set10000 and sorted actual CASE row closure',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
