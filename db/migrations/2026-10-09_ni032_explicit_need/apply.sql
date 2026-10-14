@@001_need.sql
@@002_binding.sql
@@003_continuation.sql
@@004_wave.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_NEED','RRL_STOCK_REPL_BIND','RRL_STOCK_REPL_CONTINUATION','RRL_STOCK_WAVE_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=8 then raise_application_error(-20808,'EXPLICIT_TARGET_NEED_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-047-explicit-target-need' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit replenishment uses its own CASE remaining demand and usable target coverage; storage HARD is not target supply',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
