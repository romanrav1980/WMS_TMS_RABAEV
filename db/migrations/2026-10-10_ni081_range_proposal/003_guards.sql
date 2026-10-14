create or replace trigger RRL_PR_OPERATION_G before insert or update or delete on RRL_PICK_RANGE_OPERATION for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1 then raise_application_error(-20863,'PICK_RANGE_IMMUTABLE_API_ONLY');end if;
end;
/
create or replace trigger RRL_PR_PROPOSAL_G before insert or update or delete on RRL_PICK_RANGE_PROPOSAL for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1 then raise_application_error(-20863,'PICK_RANGE_IMMUTABLE_API_ONLY');end if;
end;
/
create or replace trigger RRL_PR_CANCEL_G before insert or update or delete on RRL_PICK_RANGE_CANCEL for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1 then raise_application_error(-20863,'PICK_RANGE_IMMUTABLE_API_ONLY');end if;
end;
/
