prompt [migration 2026-05-17-003] Safe rollback
prompt This rollback only removes the PL/SQL API package. It does not drop data tables or columns.
prompt Drop table/column rollback is intentionally not automated because it would destroy regulatory data.

declare
  n number;
begin
  select count(*) into n
    from user_objects
   where object_name = 'RRL_REGULATORY_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_REGULATORY_API';
  end if;
end;
/

update RRL_SCHEMA_MIGRATIONS
   set STATUS = 'ROLLED_BACK',
       NOTES = 'Safe rollback: dropped RRL_REGULATORY_API only; tables and columns retained.'
 where MIGRATION_ID = '2026-05-17-003-regulatory-lifecycle-entities';

commit;

prompt [migration 2026-05-17-003] Safe rollback finished.
