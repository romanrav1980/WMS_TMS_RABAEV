merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-177-slot-repacking'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Atomic packing of two measured occupied places into parent slot through existing HU attach/placement/reservation owners',sysdate,user,
'db/migrations/2026-10-11_ni041_slot_repack/apply.sql','db/migrations/2026-10-11_ni041_slot_repack/rollback.sql','APPLIED',
'Owned411/HU.REPACK177:61016ccdb0; actual CASE12+parent8/two claims->one30kg/P20H20/HELD tare2; capacity late refusal rollback and native rollback restore sources; concurrent HTTP one receipt, existing sync retry and unpack reverse; native cleanup/deferred DONE/ownP0; original135P20H20');
commit;
