prompt [migration 2026-05-19-031] wave pick task fact and minimax trigger - verify

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_TASK'
   and column_name in ('FACT_QTY', 'DONE_BY')
 order by column_id;

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_WAVE_TASK'
   and column_name in ('FACT_QTY', 'DONE_AT', 'DONE_BY')
 order by column_id;

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-031-wave-pick-task-fact-minimax-trigger';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-19-031] verify done
