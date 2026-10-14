@@001_readiness.sql
@@002_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_WAVE_READY','RRL_STOCK_WAVE_PICK_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'COVERED_REPLENISHMENT_RELEASE_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-043-covered-replenishment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Cancel only unallocated unstarted replenishment placeholders already covered by actual owned wave stock; no P/H effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
