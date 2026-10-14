merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-270-multi-pallet-st-assignment'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing native ST assignment supports multiple pallet rows and preserves loaded groups',sysdate,user,
'db/migrations/2026-10-11_ni022_multi_st/apply.sql','db/migrations/2026-10-11_ni022_multi_st/rollback.sql','APPLIED',
'Two owned planning pallets sameST assigned existing33564/native outerrollback/HTTPrepeat/48EA20kg2packs/P20H20. Mixedloaded currentgroup preserved/new unassignedsameST refused under temporary config fullyrolledback. Old259time source stale now. NativeVALID/steady1.127ms.');
commit;
