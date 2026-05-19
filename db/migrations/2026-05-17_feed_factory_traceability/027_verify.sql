prompt [migration 2026-05-17-027] warehouse task quantity mode - verify

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_WAREHOUSE_TASK'
   and column_name in ('QTY_MODE', 'FACT_QTY', 'PARENT_TASK_ID')
 order by column_name;

select index_name, uniqueness
  from user_indexes
 where table_name = 'RRL_WAREHOUSE_TASK'
   and index_name in ('RRL_WAREHOUSE_TASK_I5', 'RRL_WAREHOUSE_TASK_I6')
 order by index_name;

select QTY_MODE, STATUS, count(*) TASK_COUNT
  from RRL_WAREHOUSE_TASK
 group by QTY_MODE, STATUS
 order by QTY_MODE, STATUS;

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-027] verify done
