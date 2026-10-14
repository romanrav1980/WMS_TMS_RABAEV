merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-216-load-tare-return-recovery'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original accepted vehicle tare return funds new original CASE hold before stock unloading',sysdate,user,'db/migrations/2026-10-11_ni063_load_recovery/apply.sql','db/migrations/2026-10-11_ni063_load_recovery/rollback.sql','APPLIED',
'Actual CASE1118/wave472/WARE38255845/original nested tare transfer1/accepted vehicle return1/warehouse physical2(initial2)/new HELD1/old transferred unchanged; late rollback/concurrent recovery/replay/currentWARE403; subsequent whole slotted unloadP7H7/14codes/new links2/original-7 retained/native cleanup0/protected13520/20. Scoped API history and two load indexes.');
commit;
