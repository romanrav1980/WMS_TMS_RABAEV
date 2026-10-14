@@001_schema.sql
@@002_guards.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-114-linked-expense-corrections' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Append signed correction to original confirmed expense, original total lock/current final recheck/dual decisions/signed allocation; old charge retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
