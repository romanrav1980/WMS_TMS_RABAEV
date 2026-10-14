-- Dev code checkpoint only. Retain additive evidence; policy rollback requires warehouse release decision.
drop trigger RRL_QC_SAMPLE_GUARD
/
@@../2026-10-08_stock_posting_core/336_checkpoint_sampling_policy.sql
@@../2026-10-08_stock_posting_core/337_checkpoint_sampling_gate.sql
@@../2026-10-08_stock_posting_core/338_checkpoint_sampling_command.sql
@@../2026-10-10_ni051_mark_quality/002_mark.sql
@@../2026-10-10_ni051_mark_quality/005_guard.sql
@@../2026-10-10_ni051_independent_control/005_guard.sql
drop package RRL_STOCK_QC_ITEM
/
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-064-persistent-quality-sampling';
commit;
/