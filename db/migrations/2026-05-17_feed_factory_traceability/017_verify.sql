prompt [migration 2026-05-17-017] verify

select table_name
  from user_tables
 where table_name in (
   'RRL_PICK_ROUTE',
   'RRL_PICK_ROUTE_CELL',
   'RRL_PICK_FACE',
   'RRL_PICK_FACE_ARTICUL'
 )
 order by table_name;

select column_name
  from user_tab_columns
 where table_name = 'RRL_PICK_TASK'
   and column_name in ('PICK_FACE_ID', 'PICK_ROUTE_CELL_ID')
 order by column_name;

select object_type, object_name, status
  from user_objects
 where object_name in ('RRL_PICK_TOPOLOGY_API', 'RRL_PICKING_API')
 order by object_type, object_name;

select RIGHT1, USER_GROUP
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in ('PICK_TOPOLOGY_VIEW', 'PICK_TOPOLOGY_EDIT')
 order by RIGHT1;

prompt [migration 2026-05-17-017] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
