merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-305-partial-loss-recovery'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Partial selected-unit recovery via existing corrections',sysdate,user,'db/migrations/2026-10-11_ni061_partial_recovery/apply.sql','db/migrations/2026-10-11_ni061_partial_recovery/rollback.sql','APPLIED','Actualfresh305 source3 marked6codes/partial1/loss2 -> twofound1 approvals/old2keys; overlap+missingQR denied/rollback/replay/firstnet1 thennet0. Same kernel/oldscan subset, currentread totals/caseselection/UI. Old303buyer3 unchanged; partialredelivery/cancellation/secondphysicalcycle next.');
commit;
