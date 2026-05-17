prompt [migration 2026-05-17-016] verify

select table_name
  from user_tables
 where table_name in (
   'RRL_PICK_PLAN',
   'RRL_PICK_PLAN_LINE',
   'RRL_PICK_TASK',
   'RRL_PICK_RESERVATION',
   'RRL_PICK_SHORTAGE',
   'RRL_PICK_DECISION_LOG'
 )
 order by table_name;

select object_type, object_name, status
  from user_objects
 where object_name = 'RRL_PICKING_API'
 order by object_type, object_name;

select right1, user_group
  from rights
 where user_group = 'GLOBAL_ADMIN'
   and upper(right1) in (
     'PICK_PLAN_VIEW',
     'PICK_PLAN_CREATE',
     'PICK_PLAN_CANCEL',
     'PICK_RESERVATION_VIEW',
     'PICK_SHORTAGE_VIEW'
   )
 order by right1;

prompt [migration 2026-05-17-016] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
