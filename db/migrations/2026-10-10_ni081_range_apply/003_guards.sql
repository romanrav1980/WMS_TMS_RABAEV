create or replace trigger RRL_RA_APPROVAL_G before insert or update or delete on RRL_PICK_RANGE_APPROVAL for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;
end;
/
create or replace trigger RRL_RA_STATUS_G before insert or update or delete on RRL_PICK_RANGE_STATUS for each row
begin
 if deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;
end;
/
create or replace trigger RRL_RA_ALLOW_REPL_G before insert or update or delete on RRL_PICK_RANGE_ALLOW_REPL for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;
end;
/
create or replace trigger RRL_RA_MEMBER_G before insert or update or delete on RRL_PICK_RANGE_MEMBER for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;
end;
/
create or replace trigger RRL_RA_DRAIN_CLOSE_G before insert or update or delete on RRL_PICK_RANGE_DRAIN_CLOSE for each row
begin
 if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;
end;
/
create or replace trigger RRL_REPL_RANGE_TARGET_G before insert or update on RRL_PICK_WAVE_REPLENISH_TASK for each row
begin
 if inserting or nvl(:new.TARGET_CELL_CODE,chr(0))!=nvl(:old.TARGET_CELL_CODE,chr(0))
  or nvl(:new.ARTICUL,chr(0))!=nvl(:old.ARTICUL,chr(0))or nvl(:new.QTY,0)>nvl(:old.QTY,0)then
  if RRL_PICK_RANGE_POLICY.target_write_allowed(:new.TARGET_CELL_CODE,:new.ARTICUL,:new.PICK_WAVE_REPLENISH_TASK_ID,:new.QTY)!=1 then
   raise_application_error(-20886,'PICK_RANGE_FUTURE_REPLENISHMENT_BLOCKED');end if;
 end if;
end;
/

