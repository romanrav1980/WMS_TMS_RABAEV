prompt [migration 2026-05-17-004] Safe rollback
prompt This rollback only removes the PL/SQL API package. It does not drop API audit data.

declare
  n number;
begin
  select count(*) into n
    from user_objects
   where object_name = 'RRL_API_AUDIT_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_API_AUDIT_API';
  end if;
end;
/

update RRL_SCHEMA_MIGRATIONS
   set STATUS = 'ROLLED_BACK',
       NOTES = 'Safe rollback: dropped RRL_API_AUDIT_API only; RRL_API_CALL_LOG retained.'
 where MIGRATION_ID = '2026-05-17-004-api-audit-replay';

commit;

prompt [migration 2026-05-17-004] Safe rollback finished.
