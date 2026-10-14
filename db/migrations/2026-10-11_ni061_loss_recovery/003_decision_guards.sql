create or replace trigger RRL_IW_RECOVERY_REQUEST_G before insert or update or delete on RRL_INTERWARE_RECOVERY_REQUEST for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_RECOVERY_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_REPORT');
end;
/
create or replace trigger RRL_IW_RECOVERY_APPROVAL_G before insert or update or delete on RRL_INTERWARE_RECOVERY_APPROVAL for each row
begin
 if updating or deleting then raise_application_error(-20863,'INTERWARE_RECOVERY_HISTORY_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_APPROVE');
end;
/
