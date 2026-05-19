prompt [migration 2026-05-19-033] dynamic pick-face assignments - verify

select table_name
  from user_tables
 where table_name = 'RRL_PICK_FACE_ASSIGNMENT';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_PICK_FACE_ASSIGN_SQ';

select index_name, uniqueness
  from user_indexes
 where index_name in ('RRL_PICK_FACE_ASSIGN_I1', 'RRL_PICK_FACE_ASSIGN_I2', 'RRL_PICK_FACE_ASSIGN_U1')
 order by index_name;

select migration_id, script_name
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-033-dynamic-pick-face-assignments';

select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;

prompt [migration 2026-05-19-033] verify done
