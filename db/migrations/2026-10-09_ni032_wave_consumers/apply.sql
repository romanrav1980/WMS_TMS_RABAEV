prompt Existing generic replenishment to existing CASE consumers, atomic root
@@002_reserve.sql
@@003_units.sql
@@001_binding.sql
@@004_task_plan.sql
@@005_task_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-021-wave-consumer-binding' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Delivered generic wave coverage bound to existing CASE demand; surplus freed in same root transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
