merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1191-loading-floor' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Immutable physical TOP tare proof in same Root loading transaction and current normative departure check; no child count multiplication',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
