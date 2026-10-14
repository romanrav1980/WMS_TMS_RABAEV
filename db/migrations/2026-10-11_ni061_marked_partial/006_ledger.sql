merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-292-marked-partial-receipt'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Exact marked subset in original interwarehouse partial receipt',sysdate,user,'db/migrations/2026-10-11_ni061_marked_partial/001_unit_core.sql','db/migrations/2026-10-11_ni061_marked_partial/rollback.sql','APPLIED','Native selectedunit-quantity/profile matrix/capturedpartial unitmove; birth/codes retained. Actualsource3/6codes received1/2profiles/remaining2ISSUED, rollback/race/replay/PUTP1/currentnotready/custody409. No Gov/hardware/independentclaim.');
commit;
