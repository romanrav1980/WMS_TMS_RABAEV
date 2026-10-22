whenever sqlerror exit failure rollback
@@verify.sql
@@before.sql
@@preflight.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-warehouse-depot-scope' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Warehouse-scoped depot configuration with existing metadata fences',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
