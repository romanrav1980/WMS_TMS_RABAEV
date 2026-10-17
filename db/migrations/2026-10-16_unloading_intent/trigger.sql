create or replace trigger RRL_UNLOAD_INTENT_GUARD
before insert or update or delete on RRL_STORE_UNLOAD_INTENT for each row
begin
 if updating or deleting then raise_application_error(-20886,'UNLOAD_INTENT_IMMUTABLE');end if;
 if not RRL_STORE_UNLOAD_API.writing then raise_application_error(-20882,'UNLOAD_INTENT_NATIVE_OWNER_REQUIRED');end if;
end;
/
