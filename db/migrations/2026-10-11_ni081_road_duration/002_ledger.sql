merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-279-road-duration-basis'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing routing matrix duration provenance',sysdate,user,
'db/migrations/2026-10-11_ni081_road_duration/001_schema.sql','db/migrations/2026-10-11_ni081_road_duration/rollback.sql','APPLIED',
'Oldrows SPEED50 default; newOSRM/Valhalla actualprofiledurations; null/fallback refused, no qty. Mockdecoder+ownOracleMERGE20.989ms2/464buf rollback; localproviders unavailable, no realroad/legalclaim.');
commit;
