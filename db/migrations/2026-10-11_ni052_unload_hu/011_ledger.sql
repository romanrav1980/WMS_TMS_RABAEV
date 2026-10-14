merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-214-whole-case-hu-unload'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Whole original CASE matryoshka predeparture unload with append-only restored nesting',sysdate,user,'db/migrations/2026-10-11_ni052_unload_hu/apply.sql','db/migrations/2026-10-11_ni052_unload_hu/rollback.sql','APPLIED',
'Actual CASE1116/wave470/outer+inner containers/original7 units14 codes/P7H7/new links2/old links2 retained/rollback/concurrent one winner/replay/currentWARE403/native cleanup0/protected13520/20. Dedicated unslotted cell; FULLPAL/storage-slot/tare custody extensions remain.');
commit;
