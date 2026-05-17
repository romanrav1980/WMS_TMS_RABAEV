-- 2026-05-17-008-traceability-spine-outbox verification

select 'TABLES' check_name,
       count(*) rows_found
  from user_tables
 where table_name in (
   'RRL_TRACE_EVENT',
   'RRL_TRACE_EDGE',
   'RRL_EVENT_OUTBOX',
   'RRL_ADAPTER_REQUEST_LOG',
   'RRL_QUALITY_HOLD'
 );

select 'SEQUENCES' check_name,
       count(*) rows_found
  from user_sequences
 where sequence_name in (
   'RRL_TRACE_EVENT_SQ',
   'RRL_TRACE_EDGE_SQ',
   'RRL_EVENT_OUTBOX_SQ',
   'RRL_ADAPTER_REQUEST_LOG_SQ',
   'RRL_QUALITY_HOLD_SQ'
 );

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_TRACEABILITY_API'
 order by object_type;

select 'MIGRATION_LEDGER' check_name,
       count(*) rows_found
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-008-traceability-spine-outbox';

select 'GLOBAL_ADMIN_RIGHTS' check_name,
       count(*) rows_found
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'TRACEABILITY_VIEW',
     'EXTERNAL_OUTBOX_VIEW',
     'EXTERNAL_OUTBOX_RETRY'
   );

select table_name, count(*) column_count
  from user_tab_columns
 where table_name in (
   'RRL_TRACE_EVENT',
   'RRL_TRACE_EDGE',
   'RRL_EVENT_OUTBOX',
   'RRL_ADAPTER_REQUEST_LOG',
   'RRL_QUALITY_HOLD'
 )
 group by table_name
 order by table_name;

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
