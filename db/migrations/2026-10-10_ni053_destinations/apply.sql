@@001_schema.sql
@@002_load_core.sql
@@003_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_HU_LOAD_CORE' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=2 then raise_application_error(-20808,'LOAD_DESTINATION_CORE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-082-loading-destination-manifest' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Freeze existing ST destination in physical loading manifest and block later loaded address change; no inferred historical addresses',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
