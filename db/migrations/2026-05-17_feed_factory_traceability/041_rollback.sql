prompt [migration 2026-05-22-041] warehouse map canvas and cell slots - rollback
prompt This migration creates data-bearing warehouse map and slot tables.
prompt Rollback is intentionally non-destructive; archive or restore from a database snapshot if physical removal is required.

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-22-041-warehouse-map-canvas-slots';

commit;

prompt [migration 2026-05-22-041] rollback done
