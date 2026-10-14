@@../2026-10-08_stock_posting_core/332_checkpoint_mark_quality_gate.sql
@@../2026-10-08_stock_posting_core/333_checkpoint_mark_quality_command.sql
@@../2026-10-10_ni051_quality_binding/001_schema.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-062-unique-mark-control';
commit;
/