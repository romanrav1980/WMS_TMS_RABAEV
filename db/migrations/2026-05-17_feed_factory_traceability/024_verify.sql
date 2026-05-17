prompt [migration 2026-05-17-024] MES raw supply planning and transfer tasks - verify

select table_name
  from user_tables
 where table_name in (
   'RRL_MES_RAW_DEMAND',
   'RRL_MES_RAW_SUPPLY_CANDIDATE',
   'RRL_MES_RAW_SHORTAGE',
   'RRL_MES_RAW_TRANSFER_TASK'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_MES_RAW_DEMAND_SQ',
   'RRL_MES_RAW_SUPPLY_CANDIDATE_SQ',
   'RRL_MES_RAW_SHORTAGE_SQ',
   'RRL_MES_RAW_TRANSFER_TASK_SQ'
 )
 order by sequence_name;

select count(*) MES_RAW_RIGHT_COUNT
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'MES_RAW_SUPPLY_VIEW',
     'MES_RAW_SUPPLY_CALCULATE',
     'MES_RAW_TRANSFER_CREATE',
     'MES_RAW_TRANSFER_CONFIRM',
     'MES_RAW_TRANSFER_CANCEL'
   );

select count(*) MIGRATION_COUNT
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-024-mes-raw-supply';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-024] verify done
