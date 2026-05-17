prompt [migration 2026-05-17-011] MES production completion - verify

select 'MES_TABLES' check_name,
       count(*) actual_count
  from user_tables
 where table_name in (
   'RRL_PRODUCTION_ORDER',
   'RRL_PROD_ORDER_BOM_LINE',
   'RRL_MES_MOVEMENT',
   'RRL_MES_COMPLETION'
 );

select 'MES_SEQUENCES' check_name,
       count(*) actual_count
  from user_sequences
 where sequence_name in (
   'RRL_PRODUCTION_ORDER_SQ',
   'RRL_PROD_ORDER_BOM_LINE_SQ',
   'RRL_MES_MOVEMENT_SQ',
   'RRL_MES_COMPLETION_SQ'
 );

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_MES_PRODUCTION_API'
 order by object_type;

select trigger_name, table_name, status
  from user_triggers
 where table_name = 'RRL_EVENTS';

select table_name, column_name, char_length
  from user_tab_columns
 where (table_name, column_name) in (
   ('RRL_EVENTS', 'UID_POLETA'),
   ('RRL_REMAINS', 'UID_POLETA'),
   ('RRL_PROD_BATCH_PALLETS', 'UID_PALLET'),
   ('RRL_CRPT_CODES', 'UID_PALLET'),
   ('RRL_CRPT_AGGREGATION', 'UID_PALLET')
 )
 order by table_name, column_name;

select 'GLOBAL_ADMIN_MES_RIGHTS' check_name,
       count(*) actual_count
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in (
     'MES_PRODUCTION_VIEW',
     'MES_PRODUCTION_EDIT',
     'MES_PRODUCTION_COMPLETE',
     'MES_WMS_BRIDGE_APPLY'
   );

select object_name, object_type, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
