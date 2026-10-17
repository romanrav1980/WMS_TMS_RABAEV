-- MIGRATION_ID: 2026-10-15-assembly-scale-recovery
-- PREPARED: coordinator independently reviews and applies with stop-on-error.
@@schema.sql
@@spec.sql
@@assembly_spec.sql
@@body.sql
@@assembly_body.sql
@@guards.sql
@@compile_verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-assembly-scale-recovery','Dual-principal assembly HOLD and observed gross reconciliation; cancel unposted step only; no stock writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
