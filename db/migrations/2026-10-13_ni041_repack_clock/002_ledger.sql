merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-011-ni041-repack-clock'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing box packing clock accepts actual HU_REPACK_SLOT root command; nonBOX remains no clock, root/state/actor/anchor checks preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
