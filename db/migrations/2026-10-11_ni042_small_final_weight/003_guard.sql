create or replace trigger RRL_PALLET_TYPE_FINAL_GUARD before insert or update of FINAL_WEIGHT_REQUIRED on RRL_PALLET_TYPE for each row
begin
 if inserting and :new.FINAL_WEIGHT_REQUIRED=0 then return;end if;
 if sys_context('RRL_PALLET_TYPE_CTX','TX_ID')is null or sys_context('RRL_PALLET_TYPE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_PALLET_TYPE_CTX','ACTOR')is null or sys_context('RRL_PALLET_TYPE_CTX','TYPE_ID')!=RRL_STOCK_PLAN_HELPER.decimal_text(:new.PALLET_TYPE_ID)
  then raise_application_error(-20863,'PALLET_TYPE_FINAL_WEIGHT_TRUSTED_OWNER_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
