@@001_schema.sql
@@002_case_return.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_CASE_RETURN_CMD' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=2 then raise_application_error(-20808,'PHYSICAL_FULFILLMENT_RETURN_INVALID');end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_ORDER_FULFILLMENT' and COLUMN_NAME in('FACT_COMPOSITION_JSON','FACT_UOM','PICKED_CASE_TASK_ID','PICKED_CONTENT_VERSION','PICKED_AT','PICKED_BY');
 if n!=6 then raise_application_error(-20808,'PHYSICAL_FULFILLMENT_COLUMNS_MISSING');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-031-physical-fulfillment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Physical CASE composition provenance on existing fulfillment; root return resets current projection',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
