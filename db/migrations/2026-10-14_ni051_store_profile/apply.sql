-- Применяет root (Codex) после review; Claude Code этот пакет не применял.
@@001_schema.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-1490-ni051-store-profile' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Versioned store profile: receiving windows, backroom, access limits; immutable change history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
