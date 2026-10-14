merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-311-sap-interware-aggregation' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Interwarehouse aggregation proof resolves exact applied SAP receipt order and line; current code-profile versions and original physical registry retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
