@@001_schema.sql
@@002_read.sql
@@003_command.sql
@@004_guards.sql
@@005_root.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_RECEIPT_READ','RRL_STOCK_STORE_RECEIPT_CMD','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'STORE_RECEIPT_INVALID');end if;
select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_RECEIPT_FACT_GUARD','RRL_STORE_RECEIPT_LINE_GUARD','RRL_STORE_RECEIPT_POLICY_GUARD','RRL_STORE_RECEIPT_USER_GUARD') and OBJECT_TYPE='TRIGGER' and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'STORE_RECEIPT_GUARDS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-083-store-barcode-receipt' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Authenticated store receiver confirms original departed ordinary whole place/barcode manifest; exact quantity fact/outbox, no second warehouse stock consumption',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
