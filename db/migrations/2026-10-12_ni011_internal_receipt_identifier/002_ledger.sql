merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-686-sap-receipt-internal-uid'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Physical SAP receipt accepts internal pallet identity; regulatory SSCC stored only with proven GS1 check digit',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
