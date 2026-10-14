create or replace trigger RRL_PICK_CREATE_OP_GUARD before insert or update or delete on RRL_PICK_PLAN_CREATE_OP for each row
begin
 if deleting then raise_application_error(-20863,'PICK_CREATE_HISTORY_IMMUTABLE');end if;
 if updating and(:old.PICK_PLAN_ID is not null or :new.OPERATION_ID!=:old.OPERATION_ID or :new.REQUEST_HASH!=:old.REQUEST_HASH or :new.ACTOR!=:old.ACTOR
  or :new.CUSTOMER_ORDER_ID!=:old.CUSTOMER_ORDER_ID or :new.WARE_ID!=:old.WARE_ID or :new.PLAN_STRATEGY!=:old.PLAN_STRATEGY
  or :new.CREATED_AT!=:old.CREATED_AT or :new.PICK_PLAN_ID is null)then raise_application_error(-20863,'PICK_CREATE_HISTORY_IMMUTABLE');end if;
 RRL_PICK_PLAN_CREATE_API.assert_write(:new.OPERATION_ID);
end;
/
