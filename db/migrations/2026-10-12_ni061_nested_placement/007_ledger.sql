merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-317-whole-hu-interware-placement' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Interwarehouse receipt creates existing oneHU task and completes whole physical tree through old HU_TASK_COMPLETE; original stock placement journal records actual base quantity',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
