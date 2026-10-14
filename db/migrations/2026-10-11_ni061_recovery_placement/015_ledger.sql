merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-301-recovery-placement'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Found goods placement using existing TASK_COMPLETE',sysdate,user,'db/migrations/2026-10-11_ni061_recovery_placement/apply.sql','db/migrations/2026-10-11_ni061_recovery_placement/rollback.sql','APPLIED','Actual ordinary+marked recovered2 placed by existing task kernel; stock conserved, native rollback and exact replay; common target cell policy, original departed trip retained. No redelivery or new government ACK.');
commit;
