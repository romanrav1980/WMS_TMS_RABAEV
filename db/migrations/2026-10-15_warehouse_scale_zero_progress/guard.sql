create or replace trigger RRL_WH_WEIGH_ZERO_GUARD
before insert or update or delete on RRL_WH_WEIGH_ZERO for each row
begin
 if updating or deleting then raise_application_error(-20886,'WH_ZERO_APPEND_ONLY');end if;
 if RRL_WH_WEIGH_REQUEST_API.writing(:new.CLAIM_ID,'ZERO')!=1 then raise_application_error(-20882,'WH_ZERO_NATIVE_INSERT_REQUIRED');end if;
end;
/
