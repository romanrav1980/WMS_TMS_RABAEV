prompt [migration 2026-05-17-013] non-destructive rollback
prompt This rollback removes only the calculated view and trigger.
prompt It intentionally keeps data columns on RRL_ARTICULS and RRL_PROD_BATCH.

declare
  procedure drop_object_if_exists(p_type varchar2, p_name varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_objects
     where object_type = upper(p_type)
       and object_name = upper(p_name);

    if n > 0 then
      execute immediate 'drop ' || p_type || ' ' || p_name;
    end if;
  end;
begin
  drop_object_if_exists('trigger', 'RRL_TRG_PROD_BATCH_SHIP_READY');
  drop_object_if_exists('view', 'RRL_PROD_BATCH_READY_V');
end;
/

commit;

prompt [migration 2026-05-17-013] rollback done
