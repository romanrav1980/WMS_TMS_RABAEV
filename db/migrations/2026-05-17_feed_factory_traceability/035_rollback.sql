prompt [migration 2026-05-19-035] case-pick TSD runtime foundation - rollback

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-035-case-pick-tsd-runtime';

prompt Runtime tables and columns are intentionally preserved.
commit;

prompt [migration 2026-05-19-035] rollback done
