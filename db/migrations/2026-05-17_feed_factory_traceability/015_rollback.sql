prompt [migration 2026-05-17-015] non-destructive rollback
prompt This rollback removes only the customer rule PL/SQL package.
prompt It intentionally keeps rule, vehicle, and shipment part tables and data.

declare
  n number;
begin
  select count(*)
    into n
    from user_objects
   where object_name = 'RRL_CUSTOMER_RULE_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_CUSTOMER_RULE_API';
  end if;
end;
/

commit;

prompt [migration 2026-05-17-015] rollback done
