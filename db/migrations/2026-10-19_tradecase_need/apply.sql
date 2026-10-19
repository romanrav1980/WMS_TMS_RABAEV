whenever sqlerror exit failure rollback
alter table RRL_TRADE_DOCUMENT drop constraint RRL_TRADE_DOC_KIND;
alter table RRL_TRADE_DOCUMENT add constraint RRL_TRADE_DOC_KIND check(ENTITY_TYPE in('OWNER','SKU','RECIPIENT','ORDER','TRIP','SUPPLY','NEED'));
@@001_documents.sql
declare n number;begin select count(*)into n from user_errors where NAME='RRL_TRADE_DOCUMENT_API';if n<>0 then raise_application_error(-20999,'TRADE_NEED_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-need'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Versioned recipient demand snapshots; no stock movements or topup orders',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
