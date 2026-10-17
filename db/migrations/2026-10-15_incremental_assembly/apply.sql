-- MIGRATION_ID: 2026-10-15-incremental-assembly
-- PREPARED: root must review all current sources/checkpoint and run stop-on-error OracleApply.
@@schema.sql
@@assembly_spec.sql
@@scale_packet_spec.sql
@@scale_packet_body.sql
@@assembly_body.sql
@@guards.sql
@@case_scale_admission_body.sql
@@stock_case_pick_body.sql
@@compile_verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-incremental-assembly','Stateful gross assembly steps; explicit operator consent; canonical CASE single writer; no stock effects on archive',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
