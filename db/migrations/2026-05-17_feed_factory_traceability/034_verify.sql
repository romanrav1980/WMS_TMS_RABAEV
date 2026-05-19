prompt [migration 2026-05-19-034] resource management foundation - verify

select table_name
  from user_tables
 where table_name in (
   'RRL_RESOURCE_TYPE',
   'RRL_RESOURCE_EQUIPMENT',
   'RRL_RESOURCE',
   'RRL_RESOURCE_SHIFT',
   'RRL_RESOURCE_SESSION',
   'RRL_RESOURCE_ASSIGNMENT',
   'RRL_RESOURCE_FACT_EVENT'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_RESOURCE_EQUIPMENT_SQ',
   'RRL_RESOURCE_SQ',
   'RRL_RESOURCE_SHIFT_SQ',
   'RRL_RESOURCE_SESSION_SQ',
   'RRL_RESOURCE_ASSIGN_SQ',
   'RRL_RESOURCE_FACT_EVENT_SQ'
 )
 order by sequence_name;

select resource_type, resource_class, resource_name, active
  from RRL_RESOURCE_TYPE
 order by resource_class, resource_type;

select column_name
  from user_tab_columns
 where table_name = 'RRL_WAREHOUSE_TASK'
   and column_name in (
     'RESOURCE_ID',
     'RESOURCE_SESSION_ID',
     'EQUIPMENT_ID',
     'PLANNED_START_AT',
     'PLANNED_FINISH_AT',
     'DISPATCH_PRIORITY'
   )
 order by column_name;

select right1, user_group
  from RIGHTS
 where user_group = 'GLOBAL_ADMIN'
   and upper(right1) in (
     'RESOURCE_MANAGEMENT_VIEW',
     'RESOURCE_MANAGEMENT_EDIT',
     'RESOURCE_SHIFT_VIEW',
     'RESOURCE_SHIFT_EDIT',
     'RESOURCE_SESSION_VIEW',
     'RESOURCE_SESSION_MANAGE',
     'RESOURCE_GANTT_VIEW',
     'RESOURCE_GANTT_REPLAN',
     'RESOURCE_DISPATCH_MANAGE',
     'WAREHOUSE_TASK_FORCE_ASSIGN'
   )
 order by right1;

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-034-resource-management-foundation';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-19-034] verify done
