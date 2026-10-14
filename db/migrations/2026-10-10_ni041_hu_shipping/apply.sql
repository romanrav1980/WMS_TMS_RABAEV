@@001_schema.sql
@@003_case_acl.sql
@@002_shipping_core.sql
@@004_hu_shipping.sql
@@005_root.sql
@@006_link_guard.sql
@@007_hu_read.sql
@@008_container_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_SHIP_CMD','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'HU_SHIPPING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-067-hu-case-shipping' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Atomic top CASE HU shipping through existing resolved ST core; immutable departure composition/history; standalone nested shipment denied',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
