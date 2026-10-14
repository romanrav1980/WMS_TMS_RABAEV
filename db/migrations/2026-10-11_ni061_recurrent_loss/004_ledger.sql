merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-304-recurrent-loss-event-keys'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Loss/recovery journals keyed by event and unit with active-loss admission',sysdate,user,'db/migrations/2026-10-11_ni061_recurrent_loss/apply.sql','db/migrations/2026-10-11_ni061_recurrent_loss/rollback.sql','APPLIED','Both newPK VALID, old2 loss+2 recovery rows retained, active0, forgeddirectinsertdenied/allVALID/P20H20. Same UNITmutex and native recapture. Second physical cycle remains acceptance pending.');
commit;
