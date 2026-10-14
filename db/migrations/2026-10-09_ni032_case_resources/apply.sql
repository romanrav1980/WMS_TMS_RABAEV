prompt NI03.2 CASE operator, qualification and session ownership
@@001_policy.sql
@@002_warehouse_policy.sql
@@../2026-10-08_stock_posting_core/142_metadata_fence.sql
@@../2026-10-08_stock_posting_core/033_task_plan.sql
@@../2026-10-08_stock_posting_core/160_case_pick_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-016-case-resources' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'CASE operator resource/session qualification and explicit handoff owner; common physical step exclusion',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
