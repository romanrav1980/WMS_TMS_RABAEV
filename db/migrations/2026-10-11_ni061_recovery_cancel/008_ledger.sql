merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-307-recovery-cancel'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable recovery finding cancellation before physical receipt',sysdate,user,'db/migrations/2026-10-11_ni061_recovery_cancel/apply.sql','db/migrations/2026-10-11_ni061_recovery_cancel/rollback.sql','APPLIED','Actual approved claim cancelled/rollback/replay/collision/retainedhistory/quota restored/samekey re-report; old cancelled approval cannotreceive, physical receipt cannotcancel/noP-noUnits. SameLOSSROW/UNITmutex/currentcontroller; concurrent cancel-vs-receive notyetexecuted.');
commit;
