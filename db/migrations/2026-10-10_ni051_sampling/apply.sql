@@001_schema.sql
@@003_mark.sql
@@002_item_proof.sql
@@004_policy.sql
@@005_gate.sql
@@006_quality.sql
@@007_sample_guard.sql
@@008_stamp_guard.sql
@@009_ware_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_QC_MARK','RRL_STOCK_QC_ITEM','RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_PALLET_QC_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=10 then raise_application_error(-20808,'PERSISTENT_SAMPLING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-064-persistent-quality-sampling' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Stable random carrier sample/sticky assignment, metadata-only root control PLAN, exact ordinary barcode/UOM proof and mandatory full rescan after QC failure',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/