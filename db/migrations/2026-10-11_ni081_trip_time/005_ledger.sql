merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-248-approved-original-trip-time'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable approval of original ARM wall-time region and current source hash',systimestamp,user,
'db/migrations/2026-10-11_ni081_trip_time/apply.sql','db/migrations/2026-10-11_ni081_trip_time/rollback.sql','APPLIED',
'Own33564 original12/native rollback/replay/sourcechanged/stale chain gate/regenerate/concurrent HTTP one version; own33565 new Cyrillic planned state/native manual fact end boundary and unfinished actual overlap; peer cancelled/facts retained; no goods/protected20-20; operational admission remains false.');
/

commit;
