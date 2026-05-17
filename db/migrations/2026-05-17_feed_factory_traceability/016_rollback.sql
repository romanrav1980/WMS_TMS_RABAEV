prompt [migration 2026-05-17-016] non-destructive rollback
prompt This rollback removes only the picking PL/SQL package.
prompt It intentionally keeps picking plans, reservations, tasks, shortages, and decision logs.

declare
  n number;
begin
  select count(*)
    into n
    from user_objects
   where object_name = 'RRL_PICKING_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_PICKING_API';
  end if;
end;
/

commit;

prompt [migration 2026-05-17-016] rollback done
