merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-175-case-slot-relocation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing native CASE same-cell slot relocation preserving goods and reservations',sysdate,user,'db/migrations/2026-10-11_ni041_case_relocation/apply.sql','db/migrations/2026-10-11_ni041_case_relocation/rollback.sql','APPLIED','Owned409 CASE1048 12 + CASE1049 8; real parent placement/unpack then native rollback/concurrent HTTP CASE slot relocation once/no quantity journal/P20H20; native return/tare release/deferred finish and own stock0');
commit;
