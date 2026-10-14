@@001_shipping_core.sql
@@002_hu_shipping.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_SHIPPING_CORE','RRL_STOCK_HU_SHIP_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'FULLPAL_HU_SHIPPING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-075-fullpal-hu-shipping' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Whole upper HU shipment through existing CASE and physically bound FULLPAL STs; exact physical tree coverage and current stock version',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
