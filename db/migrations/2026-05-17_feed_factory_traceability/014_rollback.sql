prompt [migration 2026-05-17-014] non-destructive rollback
prompt This rollback removes only the PL/SQL package.
prompt It intentionally keeps customer/order tables and data.

declare
  n number;
begin
  select count(*)
    into n
    from user_objects
   where object_name = 'RRL_CUSTOMER_ORDER_API'
     and object_type = 'PACKAGE';

  if n > 0 then
    execute immediate 'drop package RRL_CUSTOMER_ORDER_API';
  end if;
end;
/

commit;

prompt [migration 2026-05-17-014] rollback done
