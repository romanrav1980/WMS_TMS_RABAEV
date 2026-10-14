merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-234-original-marked-store-return-receiving'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original marked store return restores exact original units into blocked receiving cell',sysdate,user,'db/migrations/2026-10-11_ni062_marked_receiving/apply.sql','db/migrations/2026-10-11_ni062_marked_receiving/rollback.sql','APPLIED','Actual RET234.RECEIVE:13508027ed1 P1H0/original1key2profiles same birth codes6/current return UID AVAILABLE11/other2ISSUED10/one event/rollback/concurrent/replay/current warehouse403/protected20-20. No government or financial ERP ACK.');
commit;
