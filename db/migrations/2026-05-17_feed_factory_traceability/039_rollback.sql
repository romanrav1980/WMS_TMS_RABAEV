prompt [migration 2026-05-20-039] topology gate distance matrix - rollback
prompt This migration creates data-bearing topology gate and distance matrix tables.
prompt Rollback is intentionally non-destructive; archive or restore from a database snapshot if physical removal is required.

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-039-topology-gate-distance-matrix';

commit;

prompt [migration 2026-05-20-039] rollback done
