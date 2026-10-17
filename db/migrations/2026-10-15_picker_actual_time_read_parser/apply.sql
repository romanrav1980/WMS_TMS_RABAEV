-- Forward READ BODY-only repair; no clock, task, source or stock writes.
@@before.sql
declare n number;begin
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-picker-time-read-parser';
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_READ_PARSER_LEDGER_EXISTS');end if;
end;
/
@@body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-15-picker-time-read-parser','Strict ISO6 aware private parser avoids Oracle FX FF6 numeric-length quirk; READ BODY only',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
