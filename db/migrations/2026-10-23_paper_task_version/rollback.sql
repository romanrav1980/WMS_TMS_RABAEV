whenever sqlerror exit failure rollback
@@verify.sql
@@before_rrl_stock_hu_task.sql
@@before_rrl_stock_case_move_cmd.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-paper-task-version' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Validate the optional printed warehouse task version for HU and deferred CASE execution; preserve exact replay',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
