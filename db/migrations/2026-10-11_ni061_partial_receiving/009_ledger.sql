merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-291-interware-partial-receipt'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing ordinary partial interwarehouse receipt and same PUT',sysdate,user,'db/migrations/2026-10-11_ni061_partial_receiving/001_schema.sql','db/migrations/2026-10-11_ni061_partial_receiving/rollback.sql','APPLIED','Uniqueplan/load/unload retained; source3 received1 freshUID short2/custodypending. Native rollback/concurrent200-409/replay/PUTP1/protected20-20. Markedsubset/resolution/recovery/fullindependent notclaimed.');
commit;
