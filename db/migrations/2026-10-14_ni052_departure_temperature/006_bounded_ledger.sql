merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1173-thermal-bounded-query' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Replace measured slow thermal JSON_TABLE with bounded200 named IN parameters and close dynamic cursor on every outcome',sysdate,user,'apply_bounded_query.sql','rollback_bounded_query.sql','APPLIED');
/
