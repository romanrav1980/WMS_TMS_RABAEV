merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-313-nested-binding-scope' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Nested HU onward lookup uses current warehouse and cell, excludes applied historical bindings, and uses bounded source indexes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
