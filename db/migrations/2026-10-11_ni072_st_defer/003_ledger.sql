merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-276-unpicked-st-deferral'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Atomic original unpicked ST reassignment and immutable reason',sysdate,user,
'db/migrations/2026-10-11_ni072_st_defer/002_api.sql','db/migrations/2026-10-11_ni072_st_defer/rollback.sql','APPLIED',
'Original unassign/validated assign one UOW; currentWARE/version/cargo hash/sorted locks; actualSAP2046 two planned48EA Nov3-Nov4; outerrollback/concurrent winner/replay/collision/P20H20. No stock/physicaldispatch/fullNS58 acceptance.');
commit;
