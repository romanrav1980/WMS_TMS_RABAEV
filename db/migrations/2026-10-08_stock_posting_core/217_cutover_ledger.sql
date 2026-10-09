declare n number;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='ACTIVE' and BASELINE_ID='B0-20261009-STOCK-V2';
 if n!=1 then raise_application_error(-20808,'CUTOVER_LEDGER_REQUIRES_ACTIVE_B0');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_INVARIANT_CORE' and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'INVARIANT_FIX_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(
 select '2026-10-09-005-stock-posting-cutover' MIGRATION_ID,'RABAEV dev B0 empty stock cutover, compatibility OFF, all 31 writers classified' DESCRIPTION,'214_cutover.sql' SCRIPT_NAME,'214_cutover_rollback.sql' ROLLBACK_SCRIPT from dual
 union all select '2026-10-09-006-invariant-json-column','Correct reserved UID JSON_TABLE column in runtime invariant; verified real posted stock','216_invariant_uid_apply.sql','216_invariant_uid_rollback.sql' from dual
)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,s.DESCRIPTION,sysdate,user,s.SCRIPT_NAME,s.ROLLBACK_SCRIPT,'APPLIED');
commit;
/
