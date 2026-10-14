@@001_schema.sql
@@002_projection.sql
@@003_shipping.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_FULFILLMENT_FACT','RRL_STOCK_SHIPPING_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'SHIPPED_FACT_PROJECTION_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-032-shipped-facts' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Fulfillment shipped facts from confirmed BASE allocations; exact composition and operation provenance',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
