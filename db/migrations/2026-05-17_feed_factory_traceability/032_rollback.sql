prompt [migration 2026-05-19-032] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-032-wave-replenishment-queue-statuses';

commit;

prompt RRL_PICK_WAVE_REPLENISH_TASK queue statuses are intentionally preserved.
prompt [migration 2026-05-19-032] rollback done
