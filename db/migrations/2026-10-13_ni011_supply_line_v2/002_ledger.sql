merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-905-ni011-supply-line-v2'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit gateway v2 item lines with shared unchanged legacy article row; v1 parser unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
