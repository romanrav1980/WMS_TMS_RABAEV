create or replace trigger RRL_RESOURCE_INTENT_GUARD before insert or update or delete on RRL_RESOURCE_INTENT_ABANDON for each row begin
 if updating or deleting or RRL_RESOURCE_INTENT_API.write_allowed(:new.CONTROL_OPERATION_ID,:new.DOMAIN,:new.ORIGINAL_OPERATION_ID)!=1 then
  raise_application_error(-20863,'RESOURCE_INTENT_APPEND_ONLY');end if;
end;
/
