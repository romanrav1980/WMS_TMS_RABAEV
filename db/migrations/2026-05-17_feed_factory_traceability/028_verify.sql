prompt [migration 2026-05-17-028] warehouse task domain sync - verify

select table_name
  from user_tables
 where table_name = 'RRL_WAREHOUSE_TASK_SYNC';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_WH_TASK_SYNC_SQ';

select index_name, uniqueness
  from user_indexes
 where table_name = 'RRL_WAREHOUSE_TASK_SYNC'
 order by index_name;

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_WAREHOUSE_TASK_SYNC'
 order by column_id;

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-028] verify done
