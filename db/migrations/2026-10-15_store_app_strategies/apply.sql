-- MIGRATION_ID: 2026-10-15-store-app-strategies
@@mode_constraint.sql
@@rrl_stock_store_receipt_read.sql
@@rrl_stock_store_receipt_cmd.sql
@@rrl_stock_store_weight_core.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-store-app-strategies' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Standalone store app scoped receiver and explicit PAPER_COUNT strategy',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
