@@001_schema.sql
@@002_disposition.sql
@@003_receipt_command.sql
@@004_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_DISPOSITION','RRL_STOCK_STORE_RECEIPT_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'STORE_DISPOSITION_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-086-store-receipt-disposition' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Exact per-original BASE receipt disposition, immutable discrepancy and missing/return/excess obligations; original shipment and warehouse stock unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/

@@005_case_cursor_index.sql
