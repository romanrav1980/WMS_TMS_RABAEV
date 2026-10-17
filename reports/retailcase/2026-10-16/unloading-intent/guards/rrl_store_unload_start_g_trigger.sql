create or replace trigger RRL_STORE_UNLOAD_START_G before insert or update or delete on RRL_STORE_UNLOAD_START for each row
begin if not inserting or not RRL_STORE_UNLOAD_API.writing then raise_application_error(-20863,'UNLOAD_START_HISTORY_IMMUTABLE');end if;end;
/
