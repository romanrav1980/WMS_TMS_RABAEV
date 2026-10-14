merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-181-sap-putaway-identity'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Preserve non-SAP residual task identity; distinguish SAP putaway by immutable pallet UID',sysdate,user,
'db/migrations/2026-10-11_ni042_sap_task_identity/apply.sql','db/migrations/2026-10-11_ni042_sap_task_identity/rollback.sql','APPLIED',
'Fresh original index DDL/checkpoint; replacement built before old removal; live UNIQUE VALID; actual two distinct SAP putaway task facts coexist, weighted ARTMAS/gateway supply/P9.8/unit1/replay; cleanup by existing cancel/native count, no stock DML');
commit;
