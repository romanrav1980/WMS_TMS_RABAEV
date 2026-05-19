prompt [migration 2026-05-19-036] warehouse task stock move ledger - rollback

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-036-warehouse-task-stock-move-ledger';

prompt Stock-move ledger table is intentionally preserved.
commit;

prompt [migration 2026-05-19-036] rollback done
