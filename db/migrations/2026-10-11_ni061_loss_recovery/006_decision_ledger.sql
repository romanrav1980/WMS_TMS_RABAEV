merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-299-loss-recovery-decisions'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found confirmed-lost goods report and independent approval',sysdate,user,'db/migrations/2026-10-11_ni061_loss_recovery/001_schema.sql','db/migrations/2026-10-11_ni061_loss_recovery/rollback_decisions.sql','APPLIED','Actual ordinary/marked wholelost2 report/independentapproval/rollback/race/replay; no stock before physicalreceive300. CurrentWARE/exactunitversions/lossbook; noGovACK/hardware/industrialclaim.');
commit;
