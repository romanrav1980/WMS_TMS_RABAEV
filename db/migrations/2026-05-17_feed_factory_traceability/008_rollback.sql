prompt [migration 2026-05-17-008] Traceability spine and event outbox - safe rollback

declare
  n number;
begin
  select count(*) into n
    from user_objects
   where object_name = 'RRL_TRACEABILITY_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_TRACEABILITY_API';
  end if;
end;
/

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-008-traceability-spine-outbox';

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'TRACEABILITY_VIEW',
     'EXTERNAL_OUTBOX_VIEW',
     'EXTERNAL_OUTBOX_RETRY'
   );

commit;

prompt [migration 2026-05-17-008] Safe rollback finished.
prompt Data tables, sequences, indexes, trace history, outbox rows, adapter logs, and QA holds were intentionally kept.
