prompt NI03.2 explicit qualifications and observed nearest resource
@@001_schema.sql
@@002_policy.sql
@@../2026-10-08_stock_posting_core/142_metadata_fence.sql
@@006_task_core.sql
@@003_recovery.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-011-resource-qualification' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI03.2 explicit resource task qualification, observed cell and nearest free assignment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
