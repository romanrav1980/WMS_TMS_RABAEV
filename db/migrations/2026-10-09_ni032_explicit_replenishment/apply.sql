@@001_binding.sql
@@002_continuation.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_BIND','RRL_STOCK_REPL_CONTINUATION') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'EXPLICIT_REPLENISHMENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-044-explicit-replenishment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit CASE replenishment releases surplus coverage; continuation resets parent frozen source wire and supports explicit normal demand',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
