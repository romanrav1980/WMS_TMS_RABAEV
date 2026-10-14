merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-206-small-case-hu-control'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Measured small CASE cargo proof retained through existing HU layout',sysdate,user,
'db/migrations/2026-10-11_ni042_small_hu/apply.sql','db/migrations/2026-10-11_ni042_small_hu/rollback.sql','APPLIED',
'Own QPB206C05567F9/type14/CASE1102/v3/SSCC090000000000000148/gross.400/tare.100/net.300: unweighed child blocked under exempt parent, measured control retained pack/whole move/unpack, operational version advances, actual7then6 correction revokes. Native cleanup13520/20; ordinary v2 policy unchanged.');
commit;
