prompt [migration 2026-05-17-030] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-030-wave-replenishment-source-reservation';

commit;

prompt Wave replenishment source reservation columns and reservation history are intentionally preserved.
prompt [migration 2026-05-17-030] rollback done
