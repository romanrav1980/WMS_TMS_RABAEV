merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-302-recovery-redelivery'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found cargo corrective original ST and final1+2 delivery',sysdate,user,'db/migrations/2026-10-11_ni061_recovery_redelivery/apply.sql','db/migrations/2026-10-11_ni061_recovery_redelivery/rollback.sql','APPLIED','Actual ordinary+marked recovered2 existing ST/QC/load/depart/STORE; original FF3 once, buyer1+2=3, loss2/recovered2 history. Native load+store rollback/replay, codehashes unchanged; source index/shared kernel/no fake ACK.');
commit;
