@@001_schema.sql
@@002_receiver_read.sql
@@003_command.sql
@@004_root.sql
@@005_guards.sql
@@006_queue_indexes.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_RETURN_CUST_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_STORE_RECEIPT_READ') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'STORE_RETURN_CUSTODY_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-095-store-return-custody' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit authenticated driver binding/store handover/independent driver pickup, current vehicle/capacity, no anonymous driver proof or stock birth',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
