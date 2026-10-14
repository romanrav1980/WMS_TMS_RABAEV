@@001_schema.sql
@@002_guards.sql
@@003_weight_source.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-113-trip-expense-exact-allocation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Approved trip extra expense allocated exact cents on original actual STOCK manifests, vehicle expenses excluded, existing billing detail',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
