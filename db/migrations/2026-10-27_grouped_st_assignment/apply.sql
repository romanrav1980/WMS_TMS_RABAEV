@@preflight.sql
@@001_function.sql
@@compile_dependents.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-grouped-st-assignment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Bound grouped ST assignment to 1000 physical places; preserve locking and membership invariants',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
