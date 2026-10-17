-- ADDITIVE FORWARD COMPLETION ONLY: no DDL and no business/clock writes.
-- Original v3 apply installed all objects but stopped at an incorrect NORMAL-index assertion.
declare n number;begin
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-picker-actual-time-source';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_FINISH_LEDGER_ALREADY_PRESENT');end if;
end;
/
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-15-picker-actual-time-source','Explicit aware picker manual time; v3 DDL plus v4 logical TZ index verification; WORK uncertified',sysdate,user,'finish.sql','rollback.sql','APPLIED');
commit;
