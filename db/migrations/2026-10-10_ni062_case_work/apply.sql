@@001_schema.sql
@@002_command.sql
@@003_root.sql
@@004_guards.sql
@@005_history_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_STORE_CASE_CMD','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'STORE_CASE_WORK_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-091-store-case-investigation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit dispatcher deadline/separate investigators/immutable findings/independent KRO loss after shipment, no second stock subtraction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
