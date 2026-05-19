prompt [migration 2026-05-19-036] warehouse task stock move ledger - verify

select table_name
  from user_tables
 where table_name = 'RRL_WAREHOUSE_TASK_STOCK_MOVE';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_WH_TASK_STOCK_MOVE_SQ';

select constraint_name, constraint_type
  from user_constraints
 where table_name = 'RRL_WAREHOUSE_TASK_STOCK_MOVE'
   and constraint_name in (
     'RRL_WH_TASK_STOCK_MOVE_PK',
     'RRL_WH_TASK_STOCK_MOVE_U1',
     'RRL_WH_TASK_STOCK_MOVE_FK1',
     'RRL_WH_TASK_STOCK_MOVE_CHK1'
   )
 order by constraint_name;

select index_name
  from user_indexes
 where table_name = 'RRL_WAREHOUSE_TASK_STOCK_MOVE'
   and index_name in (
     'RRL_WH_TASK_STOCK_MOVE_U1',
     'RRL_WH_TASK_STOCK_MOVE_I1',
     'RRL_WH_TASK_STOCK_MOVE_I2'
   )
 order by index_name;

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-036-warehouse-task-stock-move-ledger';

prompt [migration 2026-05-19-036] verify done
