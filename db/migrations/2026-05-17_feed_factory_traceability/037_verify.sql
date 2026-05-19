prompt [migration 2026-05-20-037] replenishment release policy rules - verify

select table_name
  from user_tables
 where table_name = 'RRL_ARTICUL_REPLENISH_RULE';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_ART_REPL_RULE_SQ';

select column_name
  from user_tab_columns
 where table_name = 'RRL_PICK_FACE_ARTICUL'
   and column_name in (
     'USE_ARTICUL_REPLENISH_RULE',
     'REPLENISHMENT_RELEASE_POLICY',
     'SAFETY_LAYER_QTY',
     'PREDICTIVE_BUFFER_MIN',
     'PICK_RATE_SOURCE',
     'RECHECK_ON_PICK_EVENT'
   )
 order by column_name;

select column_name
  from user_tab_columns
 where table_name in ('RRL_PICK_WAVE_DEMAND', 'RRL_PICK_WAVE_REPLENISH_TASK')
   and column_name in (
     'REPLENISHMENT_RELEASE_POLICY',
     'SAFETY_LAYER_QTY',
     'PREDICTIVE_BUFFER_MIN',
     'PICK_RATE_SOURCE',
     'RECHECK_ON_PICK_EVENT'
   )
 order by table_name, column_name;

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-037-replenishment-release-policy-rules';

prompt [migration 2026-05-20-037] verify done
