-- MIGRATION_ID: 2026-10-15-finance-scoped-decisions
-- Preserve immutable finance guards; use native role/scope and independent object-author checks.
@@rrl_log_expense_guard.sql
@@rrl_log_exp_decision_guard.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-finance-scoped-decisions' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped expense reporting/approval and independent author; preserve immutable history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
