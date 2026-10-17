create or replace trigger RRL_DELIV_WINDOW_GUARD
before insert or update or delete on RRL_DELIVERY_WINDOW for each row
begin
 if updating or deleting then raise_application_error(-20886,'DELIVERY_TIME_IMMUTABLE');end if;
 if sys_context('RRL_DELIVERY_TIME_CTX','OPERATION_ID')is null
  or sys_context('RRL_DELIVERY_TIME_CTX','OPERATION_ID')!=:new.OPERATION_ID
  or sys_context('RRL_DELIVERY_TIME_CTX','ACTOR')is null
  or sys_context('RRL_DELIVERY_TIME_CTX','ACTOR')!=:new.ACTOR
  or nvl(sys_context('RRL_DELIVERY_TIME_CTX','ACTION'),'NONE')!='PLAN'
  or nvl(sys_context('RRL_DELIVERY_TIME_CTX','TX_ID'),'NONE')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20882,'DELIVERY_NATIVE_OWNER_REQUIRED');end if;
end;
/
