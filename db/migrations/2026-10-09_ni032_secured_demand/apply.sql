prompt Cumulative physical pick facts and non-overlapping secured demand
@@001_task_domain.sql
@@002_snapshot.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-022-secured-demand' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Cumulative pick-move BASE facts; stock allocation excludes overlap of picked fact and active HARD',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
