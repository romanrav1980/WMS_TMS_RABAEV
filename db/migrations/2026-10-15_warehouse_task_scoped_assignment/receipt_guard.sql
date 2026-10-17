create or replace trigger RRL_WTASK_COMMAND_GUARD before insert or update or delete on RRL_WTASK_RESOURCE_COMMAND for each row begin
 if updating or deleting or RRL_WTASK_ASSIGN_API.ledger_write_allowed!=1 then raise_application_error(-20863,'WTASK_COMMAND_APPEND_ONLY');end if;
end;
/
