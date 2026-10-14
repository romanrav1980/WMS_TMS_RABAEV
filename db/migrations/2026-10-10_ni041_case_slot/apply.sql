@@001_schema.sql
@@002_placement.sql
@@003_unpack.sql
@@004_slot.sql
@@005_case_move.sql
@@006_case_return.sql
@@007_shipping_core.sql
@@008_guards.sql
@@009_claim_identity_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_PLACEMENT_CORE','RRL_STOCK_HU_UNPACK_CMD','RRL_STOCK_HU_SLOT','RRL_STOCK_CASE_MOVE_CMD','RRL_STOCK_CASE_RETURN_CMD','RRL_STOCK_SHIPPING_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=12 then raise_application_error(-20808,'CASE_SLOT_PLACEMENT_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-076-case-slot-placement' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing CASE polymorphic measured slot claim and unpack; source claims released by actual move, return and shipment without fake stock pallet',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
