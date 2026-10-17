@@before_rrl_log_expense_guard.sql
@@before_rrl_log_exp_decision_guard.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-finance-scoped-decisions';
commit;
