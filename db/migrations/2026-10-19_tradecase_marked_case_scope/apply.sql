whenever sqlerror exit failure rollback
@@001_trade_spec.sql
@@002_trade_body.sql
@@003_case_access.sql
@@004_assignment.sql
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin select count(*)into n from user_objects where STATUS='INVALID'and OBJECT_NAME not like'BIN$%';if n<>0 then raise_application_error(-20999,'TRADE_MARKED_CASE_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-marked-case-scope'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Allow scoped owned TRADECASE tobacco CASE with current resource session and unit scans',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
