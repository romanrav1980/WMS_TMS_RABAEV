whenever sqlerror exit failure rollback
@@document_api.sql
declare n number;begin
 select count(*)into n from user_errors where name='RRL_TRADE_DOCUMENT_API';
 if n<>0 then raise_application_error(-20999,'TRADECASE_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-document-journal' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(x.MIGRATION_ID,'TRADECASE durable business rejection and atomic document response outbox',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
