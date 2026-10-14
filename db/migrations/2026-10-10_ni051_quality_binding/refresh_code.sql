@@002_gate.sql
@@003_shipping.sql
@@004_quality.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_QC_GATE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_PALLET_QC_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'QUALITY_COMPOSITION_BINDING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-060-quality-composition-binding' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing QC and pallet shipment share exact physical composition; legacy BLOCK_IF_NO_PROOVE gate checks current stamps',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/