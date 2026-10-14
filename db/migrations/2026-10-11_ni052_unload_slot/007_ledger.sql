merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-215-unload-current-storage-slot'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original unloading restores real current measured storage slot through existing placement owner',sysdate,user,'db/migrations/2026-10-11_ni052_unload_slot/apply.sql','db/migrations/2026-10-11_ni052_unload_slot/rollback.sql','APPLIED',
'Actual CASE1117/wave471/WARE34189220/original2.45kg .125m3/OCCUPIED slot214/task931 DONE/SYNCED/HARD same slot; late capacity refusal rolls back full unload; native rollback/concurrent/replay/currentWARE403; original7 units14 codes/new nesting/native cleanup0/protected13520/20.');
commit;
