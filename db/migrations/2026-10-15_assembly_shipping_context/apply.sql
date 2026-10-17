-- MIGRATION_ID: 2026-10-15-assembly-shipping-context
@@before.sql
@@body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-assembly-shipping-context','Read-only own CASE prepared shipment links and final signature; no writes or authority changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
