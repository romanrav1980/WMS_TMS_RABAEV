prompt [migration 2026-05-17-002] Feed factory traceability API - verify

select migration_id, status, applied_at, applied_by
  from RRL_SCHEMA_MIGRATIONS
 where migration_id = '2026-05-17-002-feed-factory-traceability-api';

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_PRODUCTION_API'
 order by object_type;

select type, name, line, position, text
  from user_errors
 where name = 'RRL_PRODUCTION_API'
 order by sequence;

select status, count(*) object_count
  from user_objects
 where object_name not like 'BIN$%'
 group by status
 order by status;

prompt [migration 2026-05-17-002] Verify finished.
