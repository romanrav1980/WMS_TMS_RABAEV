create or replace trigger RRL_IW_RECOVERY_PUT_GUARD before insert or update or delete on RRL_IW_RECOVERY_PUT_PLAN for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_PUT_PLAN_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_PUTAWAY_PLAN');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_PUT_PLAN',:new.OPERATION_ID));
end;
/
create or replace trigger RRL_IW_RECOVERY_PLACE_GUARD before insert or update or delete on RRL_IW_RECOVERY_PLACEMENT for each row
begin
 if updating or deleting then raise_application_error(-20878,'RECOVERY_PLACEMENT_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'TASK_COMPLETE');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(:new.TASK_ID)));
end;
/
