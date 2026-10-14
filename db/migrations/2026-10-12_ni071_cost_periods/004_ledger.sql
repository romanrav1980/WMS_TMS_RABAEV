merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-512-warehouse-cost-period-partition' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'BOX recognition partitioned by actual CASE date; one immutable source claim; legacy rows preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
