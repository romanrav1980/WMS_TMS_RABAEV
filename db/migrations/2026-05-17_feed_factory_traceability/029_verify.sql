prompt [migration 2026-05-17-029] wave case-pick replenishment settings - verify

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_FACE_ARTICUL'
   and column_name in (
     'REPLENISHMENT_METHOD',
     'REPLENISHMENT_QTY_MODE',
     'MIN_TRIGGER_BOX_QTY',
     'MIN_TRIGGER_LAYER_QTY',
     'BOXES_PER_LAYER',
     'BOXES_PER_PALLET',
     'BOX_VOLUME_M3',
     'ALLOW_PARTIAL_PALLET'
   )
 order by column_id;

select column_name, data_type, nullable
  from user_tab_cols
 where table_name = 'RRL_PICK_WAVE_REPLENISH_TASK'
   and column_name in (
     'REPLENISHMENT_METHOD',
     'REPLENISHMENT_QTY_MODE',
     'RELEASE_TRIGGER_QTY',
     'BOXES_PER_LAYER',
     'BOXES_PER_PALLET',
     'BOX_VOLUME_M3',
     'PICK_FACE_MAX_VOLUME',
     'WAIT_REASON',
     'RELEASED_AT',
     'RELEASED_BY'
   )
 order by column_id;

select constraint_name, status, search_condition
  from user_constraints
 where table_name in ('RRL_PICK_FACE_ARTICUL', 'RRL_PICK_WAVE_REPLENISH_TASK')
   and constraint_name in (
     'RRL_PICK_FACE_ART_CHK3',
     'RRL_PICK_FACE_ART_CHK4',
     'RRL_PICK_FACE_ART_CHK5',
     'RRL_PICK_WAVE_REPL_CHK1',
     'RRL_PICK_WAVE_REPL_CHK2',
     'RRL_PICK_WAVE_REPL_CHK3'
   )
 order by table_name, constraint_name;

select index_name, uniqueness
  from user_indexes
 where index_name in ('RRL_PICK_FACE_ARTICUL_I2', 'RRL_PICK_WAVE_REPL_I2')
 order by index_name;

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-029-wave-case-pick-replenishment-settings';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-17-029] verify done
