create or replace trigger RRL_SAP_CAL_EX_GUARD before insert or update or delete on RRL_SAP_STORE_CAL_EXCEPTION for each row
begin
 if not inserting or RRL_STORE_CALENDAR_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'STORE_CAL_EXCEPTION_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_SAP_CAL_WRITE_GUARD before insert or update or delete on RRL_SAP_STORE_CALENDAR for each row
begin
 if RRL_STORE_CALENDAR_API.config_write_allowed!=1 then raise_application_error(-20863,'STORE_CAL_NATIVE_CONFIG_REQUIRED');end if;
end;
/
