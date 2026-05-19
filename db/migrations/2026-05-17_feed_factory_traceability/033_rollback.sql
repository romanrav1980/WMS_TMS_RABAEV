prompt [migration 2026-05-19-033] rollback is non-destructive for history

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-033-dynamic-pick-face-assignments';

commit;

prompt RRL_PICK_FACE_ASSIGNMENT is intentionally preserved.
prompt [migration 2026-05-19-033] rollback done
