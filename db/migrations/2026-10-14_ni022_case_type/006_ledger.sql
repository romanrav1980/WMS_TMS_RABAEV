merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1212-case-pallet-type' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Recipient planned type shared policy; explicit empty CASE override through existing Root/version/scans and immutable journal',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
