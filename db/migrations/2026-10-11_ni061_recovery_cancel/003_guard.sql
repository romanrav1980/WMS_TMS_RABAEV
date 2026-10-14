create or replace trigger RRL_IW_REC_CANCEL_G before insert or update or delete on RRL_IW_RECOVERY_CANCEL for each row
begin
 if updating or deleting then raise_application_error(-20863,'RECOVERY_CANCELLATION_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_CANCEL');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_CANCEL',:new.REQUEST_OPERATION_ID));
end;
/
