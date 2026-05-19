prompt [migration 2026-05-19-031] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-031-wave-pick-task-fact-minimax-trigger';

commit;

prompt Wave pick-task fact columns are intentionally preserved.
prompt [migration 2026-05-19-031] rollback done
