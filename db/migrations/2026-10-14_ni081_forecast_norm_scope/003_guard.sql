create or replace trigger RRL_WORKLOAD_SCOPE_SITE_G before insert or update or delete on RRL_WORKLOAD_SCOPE_SITE for each row
begin
 if not inserting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.OPERATION_ID)!=1 then
  raise_application_error(-20863,'WORKLOAD_SCOPE_IMMUTABLE_NATIVE_VERSION');end if;
end;
/
