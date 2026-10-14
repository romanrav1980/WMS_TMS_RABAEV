@@../2026-10-08_stock_posting_core/334_checkpoint_control_policy_gate.sql
@@../2026-10-08_stock_posting_core/335_checkpoint_control_policy_command.sql
drop trigger RRL_QC_WARE_POLICY_GUARD
/
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-063-independent-control';
commit;
/