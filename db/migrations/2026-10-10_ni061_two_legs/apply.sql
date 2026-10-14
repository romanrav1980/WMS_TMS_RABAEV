@@001_schema.sql
@@002_guards.sql
@@003_metadata.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-118-existing-trip-interwarehouse-plan' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Immutable two-leg link from existing departed standalone cargo to target warehouse/docks/existing outbound trip; no stock birth or duplicated transport assignment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
