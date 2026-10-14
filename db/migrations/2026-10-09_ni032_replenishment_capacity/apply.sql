prompt NI03.2 canonical pick-face volume and open-arrival budget
@@000_schema.sql
@@001_policy.sql
@@002_wave.sql
@@003_task_plan.sql
@@004_task_core.sql
@@005_case.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-014-replenishment-capacity' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Canonical pick-face volume including unfinished arrivals and locked physical capacity recheck',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
