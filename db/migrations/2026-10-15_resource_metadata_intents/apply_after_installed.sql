-- Only after root-confirmed installation; no schema/body recreation, compile, DROP or rollback.
@@verify_installed_indexes.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-resource-metadata-intents'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'CASE/TASK never-recorded metadata intent tombstones; no quantity effects',sysdate,user,'apply_after_installed.sql','rollback_reviewed_v2.sql','APPLIED');
commit;
