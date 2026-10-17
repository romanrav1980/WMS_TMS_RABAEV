-- MIGRATION_ID: 2026-10-15-scoped-command-lock-order
@@rrl_wave_exec_access.sql
@@rrl_stock_posting_api.sql
@@rrl_stock_store_receipt_cmd.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-scoped-command-lock-order' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Access revision guard within stock plan ownership before policy and domain locks',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
