merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-314-nested-interwarehouse-receive' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'First-leg nested one-stock-leaf cargo receipt keeps physical HU identities and appends new links with existing quantity and unit kernels; old archive preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
