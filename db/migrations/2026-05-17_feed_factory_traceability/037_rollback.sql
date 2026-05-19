prompt [migration 2026-05-20-037] replenishment release policy rules - rollback

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-037-replenishment-release-policy-rules';

prompt Replenishment release policy tables and columns are intentionally preserved.
commit;

prompt [migration 2026-05-20-037] rollback done
