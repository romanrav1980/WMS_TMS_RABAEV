prompt [migration 2026-05-23-044] ban zero warehouse id - rollback
prompt This migration intentionally deletes fixture warehouse ID 0 data and adds positive-ID constraints.
prompt Rollback does not recreate deleted fixture data. Restore from a database snapshot if those rows are needed.

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-23-044-ban-zero-warehouse-id';

commit;

prompt [migration 2026-05-23-044] rollback metadata cleanup done
