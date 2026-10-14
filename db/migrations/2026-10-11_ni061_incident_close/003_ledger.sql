merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-293-interware-incident-close'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit incident closure after full actual interwarehouse receipt',sysdate,user,'db/migrations/2026-10-11_ni061_incident_close/001_schema.sql','db/migrations/2026-10-11_ni061_incident_close/rollback.sql','APPLIED','Current target dispatcher, immutable evidence/canonical replay; full receipt+APPLIED event. Existing243 recovery/rollback/race/replay; partial292 blocked. No stock or custody change.');
commit;
