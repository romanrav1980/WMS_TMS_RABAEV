create or replace trigger RRL_TT_TIME_APPROVAL_GUARD before insert or update or delete on RRL_TT_TIME_APPROVAL for each row
begin
 if not inserting or RRL_TT_TIME_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'TT_TIME_APPROVAL_IMMUTABLE');end if;
end;
/
