prompt [migration 2026-05-17-025] MES raw supply Oracle API - verify

select object_type, object_name, status
  from user_objects
 where object_name = 'RRL_MES_RAW_SUPPLY_API'
 order by object_type;

select count(*) MIGRATION_COUNT
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-025-mes-raw-supply-api';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-025] verify done
