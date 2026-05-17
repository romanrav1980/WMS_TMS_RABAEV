prompt [migration 2026-05-17-018] verify

select table_name
  from user_tables
 where table_name in (
   'RRL_PICK_WAVE_SETTING',
   'RRL_PICK_WAVE',
   'RRL_PICK_WAVE_ORDER',
   'RRL_PICK_WAVE_LINE',
   'RRL_PICK_WAVE_RESERVATION',
   'RRL_PICK_WAVE_DEMAND',
   'RRL_PICK_WAVE_REPLENISH_TASK',
   'RRL_PICK_WAVE_TASK',
   'RRL_PICK_WAVE_SHORTAGE',
   'RRL_PICK_WAVE_AUDIT'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_PICK_WAVE_SETTING_SQ',
   'RRL_PICK_WAVE_SQ',
   'RRL_PICK_WAVE_ORDER_SQ',
   'RRL_PICK_WAVE_LINE_SQ',
   'RRL_PICK_WAVE_RES_SQ',
   'RRL_PICK_WAVE_DEMAND_SQ',
   'RRL_PICK_WAVE_REPL_SQ',
   'RRL_PICK_WAVE_TASK_SQ',
   'RRL_PICK_WAVE_SHORTAGE_SQ',
   'RRL_PICK_WAVE_AUDIT_SQ'
 )
 order by sequence_name;

select object_type, object_name, status
  from user_objects
 where object_name = 'RRL_PICK_WAVE_API'
 order by object_type, object_name;

select RIGHT1, USER_GROUP
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in (
     'PICK_WAVE_VIEW',
     'PICK_WAVE_CREATE',
     'PICK_WAVE_CALCULATE',
     'PICK_WAVE_LAUNCH',
     'PICK_WAVE_CANCEL',
     'PICK_WAVE_RELEASE_RESERVES',
     'PICK_WAVE_SETTINGS_VIEW',
     'PICK_WAVE_SETTINGS_EDIT',
     'PICK_WAVE_AUDIT_VIEW'
   )
 order by RIGHT1;

select MIGRATION_ID, DESCRIPTION
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-018-wave-picking-core';

prompt [migration 2026-05-17-018] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
