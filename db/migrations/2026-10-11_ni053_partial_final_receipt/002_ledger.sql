merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-297-partial-final-recipient'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Confirmed loss key guard and existing final recipient partial shipment lineage',sysdate,user,'db/migrations/2026-10-11_ni053_partial_final_receipt/001_unit_loss_guard.sql','db/migrations/2026-10-11_ni053_partial_final_receipt/rollback.sql','APPLIED','Actual ordinary and marked accepted1 final STORE; original3/accepted1/unreceived2/transportshort2, same originalFF. Existing229 full3 preserved; currentlossbook guarded in direct nativeUNIT trigger. No stock/GovACK/independentclaim.');
commit;
