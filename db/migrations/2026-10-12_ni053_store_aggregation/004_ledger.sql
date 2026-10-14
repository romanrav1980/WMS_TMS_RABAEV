merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-716-store-aggregation'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Store disposition uses existing registered aggregate resolver and exact issued unit/profile matrix',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
