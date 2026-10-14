@@001_schema.sql
@@004_load_core.sql
@@005_shipping_core.sql
@@002_read.sql
@@003_single_load.sql
@@006_root.sql
@@007_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOADING_READ','RRL_STOCK_SINGLE_LOAD_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'SINGLE_LOADING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-078-standalone-loading' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Standalone actual CASE/FULLPAL loading via existing ST and same shipping engine; explicit polymorphic owner FKs, current composition signature and one physical place',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
