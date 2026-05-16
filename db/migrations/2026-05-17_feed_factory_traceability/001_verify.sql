prompt [migration 2026-05-17-001] Feed factory traceability base - verify

set pagesize 300
set linesize 220
set trimspool on
set tab off

column connected_user format a20
column service_name format a20
column db_name format a15
select user connected_user,
       sys_context('USERENV','SERVICE_NAME') service_name,
       sys_context('USERENV','DB_NAME') db_name
  from dual;

column migration_id format a50
column status format a12
select migration_id, status, applied_at, applied_by
  from RRL_SCHEMA_MIGRATIONS
 where migration_id = '2026-05-17-001-feed-factory-traceability';

column table_name format a35
select table_name
  from user_tables
 where table_name in (
   'RRL_SCHEMA_MIGRATIONS',
   'RRL_SYSTEM_SETTINGS',
   'RRL_CLIENT_REG_PROFILE',
   'RRL_PROD_BATCH',
   'RRL_PROD_BATCH_PALLETS',
   'RRL_RAW_BATCH',
   'RRL_PROD_RAW_USAGE',
   'RRL_MERCURY_BATCH',
   'RRL_CRPT_CODES',
   'RRL_CRPT_AGGREGATION',
   'RRL_CRPT_AGGREGATION_ITEMS',
   'RRL_REGULATORY_OUTBOX',
   'RRL_FILE_EXCHANGE_LOG'
 )
 order by table_name;

column table_name format a30
column column_name format a30
select table_name, column_name, data_type, data_length
  from user_tab_columns
 where (table_name = 'RRL_PALLETS' and column_name in ('PROD_BATCH_ID', 'SSCC', 'MERCURY_STATUS', 'CRPT_STATUS', 'QUALITY_STATUS'))
    or (table_name = 'RRL_SBORKA_PALLET_ROWS' and column_name in ('PROD_BATCH_ID', 'SSCC', 'CRPT_TRANSFER_MODE'))
 order by table_name, column_name;

column object_type format a18
select object_type, count(*) invalid_count
  from user_objects
 where status <> 'VALID'
 group by object_type
 order by object_type;

column type format a18
column name format a40
column text format a120
select type, name, line, position, text
  from user_errors
 where name not like 'BIN$%'
 order by name, sequence;

prompt [migration 2026-05-17-001] Verify finished.

