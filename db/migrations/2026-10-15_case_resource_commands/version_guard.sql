create or replace trigger RRL_CASE_ASSIGN_VERSION_GUARD before insert or update on RRL_CASE_PICK_TASK for each row
declare
 function changed(a varchar2,b varchar2)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
 function changed_number(a number,b number)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
 function changed_time(a timestamp with time zone,b timestamp with time zone)return boolean is begin return a!=b or(a is null and b is not null)or(a is not null and b is null);end;
begin
 if inserting then
  if :new.ASSIGNMENT_VERSION is not null and :new.ASSIGNMENT_VERSION!=0 then raise_application_error(-20863,'CASE_ASSIGNMENT_VERSION_SERVER_DERIVED');end if;:new.ASSIGNMENT_VERSION:=0;return;
 end if;
 if updating('ASSIGNMENT_VERSION')then raise_application_error(-20863,'CASE_ASSIGNMENT_VERSION_SERVER_DERIVED');end if;
 if changed(:old.STATUS,:new.STATUS)or changed(:old.ASSIGNED_TO,:new.ASSIGNED_TO)
  or changed_number(:old.ASSIGNED_RESOURCE_ID,:new.ASSIGNED_RESOURCE_ID)or changed_number(:old.RESOURCE_SESSION_ID,:new.RESOURCE_SESSION_ID)
  or changed_number(:old.EQUIPMENT_ID,:new.EQUIPMENT_ID)or changed_time(:old.STARTED_AT,:new.STARTED_AT)
  or changed_time(:old.STARTED_AT_INSTANT,:new.STARTED_AT_INSTANT)or changed(:old.STARTED_SHIFT_TIME_ZONE,:new.STARTED_SHIFT_TIME_ZONE)
 then :new.ASSIGNMENT_VERSION:=:old.ASSIGNMENT_VERSION+1;else :new.ASSIGNMENT_VERSION:=:old.ASSIGNMENT_VERSION;end if;
end;
/
create or replace trigger RRL_CASE_RESOURCE_CMD_GUARD before insert or update or delete on RRL_CASE_RESOURCE_COMMAND for each row begin
 if updating or deleting or RRL_CASE_ASSIGNMENT_API.ledger_write_allowed!=1 then raise_application_error(-20863,'CASE_RESOURCE_COMMAND_APPEND_ONLY');end if;
end;
/
