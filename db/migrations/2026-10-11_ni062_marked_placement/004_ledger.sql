merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-235-original-marked-return-placement'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Reuse original marked return putaway and current cached-plan actor scope',sysdate,user,'db/migrations/2026-10-11_ni062_marked_placement/apply.sql','db/migrations/2026-10-11_ni062_marked_placement/rollback.sql','APPLIED','Actual original PUTAWAY957 DONE/SYNCED/P1H0/blockedtarget/unitAVAILABLE12/same birth codes6/native rollback/replay/nonadmin cached foreignWARE403/ERP pending. No duplicate movement or external ACK.');
commit;
