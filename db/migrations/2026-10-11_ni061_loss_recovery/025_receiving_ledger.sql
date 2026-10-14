merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-300-loss-recovery-receiving'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Physical corrective receipt of whole confirmed lost remainder via same kernel',sysdate,user,'db/migrations/2026-10-11_ni061_loss_recovery/010_receiving.sql','db/migrations/2026-10-11_ni061_loss_recovery/rollback_receiving.sql','APPLIED','Actual ordinary/marked lost2 ->newP2H0/quarantine, same two old units andsix originalcodes; native rollback/QRmissing/race/replay/collision. Historical loss intact, no customer/GovACK. Partial/recurrent and redelivery pending.');
commit;
