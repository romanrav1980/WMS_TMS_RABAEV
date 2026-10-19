whenever sqlerror exit failure rollback
@@002_api.sql
declare n number;begin
 select count(*)into n from user_errors where name='RRL_TRADE_DOCUMENT_API';
 if n<>0 then raise_application_error(-20999,'TRADECASE_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-documents' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-19-tradecase-documents','TRADECASE v1 site and versioned document intake; no physical stock writes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;