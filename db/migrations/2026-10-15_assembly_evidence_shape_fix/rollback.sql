-- Quiesce archive writers before replacing a body. No history deletion.
@@before_body.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-evidence-shape-fix';
commit;
