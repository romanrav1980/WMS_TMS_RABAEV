merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-866-ni032-same-source-bindings'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Retain separately versioned same-stock owner bindings in original whole-pallet arrival',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
