prompt [migration 2026-05-17-030] wave replenishment source reservation - verify

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_WAVE_DEMAND'
   and column_name in ('MIN_SHELF_LIFE_DAYS', 'MIN_SHELF_LIFE_PERCENT')
 order by column_id;

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_WAVE_REPLENISH_TASK'
   and column_name in (
     'SOURCE_RESERVATION_ID',
     'SOURCE_AVAILABLE_QTY',
     'SOURCE_PRODUCED_DATE',
     'SOURCE_EXPIRY_DATE',
     'MIN_SHELF_LIFE_DAYS',
     'MIN_SHELF_LIFE_PERCENT'
   )
 order by column_id;

select index_name, uniqueness
  from user_indexes
 where index_name = 'RRL_PICK_WAVE_REPL_I3';

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-030-wave-replenishment-source-reservation';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-030] verify done
