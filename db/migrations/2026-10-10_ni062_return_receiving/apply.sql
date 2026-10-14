@@001_schema.sql
@@007_return_document_schema.sql
@@003_balance_acl.sql
@@004_location_acl.sql
@@009_shared_barcode.sql
@@002_command.sql
@@005_root.sql
@@006_guards.sql
@@008_return_document_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_RETURN_REC_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_BALANCE_CORE','RRL_STOCK_LOCATION_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=8 then raise_application_error(-20808,'STORE_RETURN_RECEIVING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-096-store-return-warehouse-receipt' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Ordinary supplier/disposal store return actual blocked-cell warehouse receiving via existing balance/journal core; original SAP+pickup source, no purchase or early ERP completion',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
