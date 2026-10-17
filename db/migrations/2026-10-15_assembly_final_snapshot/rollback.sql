@@rollback_history_guard.sql
@@verify.sql
@@before_queue_body.sql
@@before_wh_body.sql
@@before_assembly_body.sql
@@before_admission_body.sql
drop package RRL_ASM_FINAL_SNAPSHOT;
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-final-snapshot'and STATUS='APPLIED';
commit;
