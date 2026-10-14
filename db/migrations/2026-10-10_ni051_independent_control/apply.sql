@@001_schema.sql
@@002_policy.sql
@@003_gate.sql
@@004_quality.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_PALLET_QC_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=6 then raise_application_error(-20808,'INDEPENDENT_CONTROL_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-063-independent-control' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Configured NONE/ANY/SCAN/WEIGHT/BOTH and independent control based on immutable actual picking actors; first check saved while auto-shipping awaits complete admission',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/