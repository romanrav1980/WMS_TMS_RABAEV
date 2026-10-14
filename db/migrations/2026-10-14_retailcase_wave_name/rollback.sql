-- Rollback restores only the previous display name; no stock effects.
lock table RRL_PICK_WAVE in row exclusive mode nowait;
update RRL_PICK_WAVE set WAVE_NAME=utl_raw.cast_to_varchar2(hextoraw('4E49434F52415F4D494E494D4158'))
where WAVE_NAME='RETAILCASE_MINIMAX';
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-retailcase-wave-name';
commit;
