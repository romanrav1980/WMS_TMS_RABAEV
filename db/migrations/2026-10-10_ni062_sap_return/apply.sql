@@001_schema.sql
@@002_command.sql
@@003_root.sql
@@004_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_RETURN_SAP_CMD','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'SAP_RETURN_BINDING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-093-sap-store-return-binding' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Original XML store return binding to approved source, warehouse recipient, exact inbox retry, no purchase or stock birth',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
