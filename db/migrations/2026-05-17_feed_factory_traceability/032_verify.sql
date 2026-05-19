prompt [migration 2026-05-19-032] wave replenishment queue statuses - verify

select constraint_name, search_condition
  from user_constraints
 where table_name = 'RRL_PICK_WAVE_REPLENISH_TASK'
   and constraint_name = 'RRL_PICK_WAVE_REPL_CHK1';

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-032-wave-replenishment-queue-statuses';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-19-032] verify done
