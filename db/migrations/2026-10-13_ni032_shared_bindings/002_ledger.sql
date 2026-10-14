merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-869-ni032-shared-bindings'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Shared whole-pallet admission checks total per-owner source bindings against unmet target demand',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
