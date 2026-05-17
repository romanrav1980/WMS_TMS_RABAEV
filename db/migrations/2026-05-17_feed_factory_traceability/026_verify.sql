prompt [migration 2026-05-17-026] warehouse reachtruck tasks - verify

select table_name
  from user_tables
 where table_name = 'RRL_WAREHOUSE_TASK';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_WAREHOUSE_TASK_SQ';

select index_name, uniqueness
  from user_indexes
 where table_name = 'RRL_WAREHOUSE_TASK'
 order by index_name;

select right1, user_group
  from rights
 where upper(right1) in ('WAREHOUSE_TASK_VIEW', 'WAREHOUSE_TASK_EXECUTE')
 order by right1, user_group;

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-026] verify done
