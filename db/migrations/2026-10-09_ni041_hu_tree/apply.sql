@@001_schema.sql
@@002_read.sql
@@003_commands.sql
@@004_balance.sql
@@005_closure.sql
@@006_eligibility.sql
@@007_posting.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_READ','RRL_STOCK_HU_CMD','RRL_STOCK_BALANCE_CORE','RRL_STOCK_PLAN_HELPER','RRL_STOCK_ELIGIBILITY','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=12 then raise_application_error(-20808,'HU_TREE_OBJECTS_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-050-warehouse-hu-tree' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Warehouse container identity reuses RRL_PALLETS; versioned single-parent links, root pack/unpack and nested quantity/source guards; regulatory aggregation retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
