@@before.sql
@@case_access_spec.sql
@@case_access_body.sql
@@meta_scope_spec.sql
@@meta_scope_body.sql
@@resource_policy_body.sql
@@case_pick_body.sql
@@assembly_body.sql
@@lifecycle_body.sql
@@compile_dependents.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-assembly-scoped-execute'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Assigned scoped ordinary-count assembly; trusted metadata and unchanged stock owner',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
