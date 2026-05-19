prompt [migration 2026-05-17-029] rollback is non-destructive

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-029-wave-case-pick-replenishment-settings';

commit;

prompt RRL_PICK_FACE_ARTICUL and RRL_PICK_WAVE_REPLENISH_TASK replenishment-setting columns are intentionally preserved.
prompt [migration 2026-05-17-029] rollback done
