whenever sqlerror exit failure rollback
@@001_documents.sql
@@002_binding.sql
@@003_context.sql
declare n number;begin select count(*)into n from user_errors where NAME in('RRL_TRADE_DOCUMENT_API','RRL_TRADE_ORDER_API','RRL_TRADE_PICK_CONTEXT');if n<>0 then raise_application_error(-20999,'TRADE_BOX_POLICY_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-box-boundaries'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Enforce recipient broken-box and partial-shipment boundaries on accepted and native demand',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
