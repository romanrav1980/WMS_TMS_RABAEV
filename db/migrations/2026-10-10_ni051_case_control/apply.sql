@@004_hu_read.sql
@@001_case.sql
@@003_gate.sql
@@002_quality.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_QC_CASE','RRL_STOCK_QC_GATE','RRL_STOCK_PALLET_QC_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'CASE_CONTROL_PROJECTION_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-065-case-control-projection' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing CASE control state/events follow actual current admission; nested QC saved without standalone auto-shipment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/