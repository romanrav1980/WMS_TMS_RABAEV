create or replace trigger RRL_IW_REC_DISPATCH_GUARD before insert or update or delete on RRL_IW_RECOVERY_DISPATCH for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_DISPATCH_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_DISPATCH',:new.OPERATION_ID));
end;
/
create or replace trigger RRL_IW_REC_ST_IMMUTABLE before update or delete on RRL_IW_RECOVERY_ST_BIND for each row
begin raise_application_error(-20878,'RECOVERY_ST_BIND_IMMUTABLE');end;
/
