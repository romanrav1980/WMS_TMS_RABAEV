prompt [migration 2026-05-19-035] case-pick TSD runtime foundation - verify

select table_name
  from user_tables
 where table_name in (
   'RRL_PALLET_TYPE',
   'RRL_CUSTOMER_PALLET_TYPE_RULE',
   'RRL_CASE_PICK_SETTING',
   'RRL_CASE_PICK_TASK',
   'RRL_CASE_PICK_LINE',
   'RRL_CASE_PICK_SHORT',
   'RRL_INVENTORY_TASK',
   'RRL_CASE_PICK_EVENT'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_PALLET_TYPE_SQ',
   'RRL_CUST_PALLET_TYPE_RULE_SQ',
   'RRL_CASE_PICK_TASK_SQ',
   'RRL_CASE_PICK_LINE_SQ',
   'RRL_CASE_PICK_SHORT_SQ',
   'RRL_INVENTORY_TASK_SQ',
   'RRL_CASE_PICK_EVENT_SQ'
 )
 order by sequence_name;

select column_name
  from user_tab_columns
 where table_name = 'RRL_PICK_WAVE_TASK'
   and column_name in ('CASE_PICK_TASK_ID', 'CASE_PICK_LINE_ID')
 order by column_name;

select PALLET_TYPE_CODE, DEFAULT_VOLUME_M3, ACTIVE
  from RRL_PALLET_TYPE
 where PALLET_TYPE_CODE in ('EURO_PALLET', 'AMERICAN_PALLET', 'TROLLEY')
 order by PALLET_TYPE_CODE;

select RIGHT1
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'CASE_PICK_VIEW',
     'CASE_PICK_EXECUTE',
     'CASE_PICK_MANAGE',
     'CASE_PICK_SHORT_APPROVE',
     'INVENTORY_TASK_VIEW',
     'INVENTORY_TASK_EXECUTE'
   )
order by RIGHT1;

select RESOURCE_TYPE, RESOURCE_CLASS, ACTIVE
  from RRL_RESOURCE_TYPE
 where RESOURCE_TYPE = 'INVENTORY';

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-035-case-pick-tsd-runtime';

prompt [migration 2026-05-19-035] verify done
