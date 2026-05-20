prompt [migration 2026-05-20-038] warehouse topology master data - rollback
prompt This migration creates data-bearing warehouse topology master data.
prompt Rollback is intentionally non-destructive; archive or restore from a database snapshot if physical removal is required.

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-038-warehouse-topology-master-data';

commit;

prompt [migration 2026-05-20-038] rollback done
