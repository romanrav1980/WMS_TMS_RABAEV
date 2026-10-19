whenever sqlerror exit failure rollback
@@001_access.sql
declare n number;begin select count(*)into n from user_errors where NAME='RRL_TRADE_CASE_ACCESS';if n<>0 then raise_application_error(-20999,'TRADE_CASE_OWNER_QUERY_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-case-owner-query'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Select CASE owner candidates by carrier return or active reservation before attribute join',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
