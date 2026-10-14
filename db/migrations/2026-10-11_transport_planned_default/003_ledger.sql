merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-253-transport-planned-default'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Correct UTF8 default planned status for original new transport tasks',sysdate,user,'db/migrations/2026-10-11_transport_planned_default/apply.sql','db/migrations/2026-10-11_transport_planned_default/rollback.sql','APPLIED','Native column default was literal questionmarks; original addfunction omitsstatus. Future insertscorrect/nooldmassrepair/directoriginalfunction rollback/noTTretained/protected20-20. Rowtype dependencies recompiled/pool restarted.');
commit;
