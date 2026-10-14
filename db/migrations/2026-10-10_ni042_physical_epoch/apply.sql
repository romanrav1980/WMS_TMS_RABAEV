@@001_schema.sql
@@002_balance.sql
@@003_unit_signature.sql
@@004_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_BALANCE_CORE','RRL_STOCK_HU_UNIT_SIGNATURE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'PHYSICAL_EPOCH_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-072-physical-stock-epoch' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Physical quantity epoch separate from reservation stock version; bounded physical unit signature for measured standalone stock',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
