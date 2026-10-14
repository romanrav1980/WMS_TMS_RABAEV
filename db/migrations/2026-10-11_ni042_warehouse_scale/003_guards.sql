create or replace trigger RRL_WH_SCALE_DEVICE_GUARD before insert or update or delete on RRL_WH_SCALE_DEVICE for each row
declare n number;v_old_ware number;actor_value varchar2(50):=sys_context('RRL_STOCK_WRITE_CTX','ACTOR');
begin
 if sys_context('RRL_STOCK_WRITE_CTX','MODE')is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='CONFIG'
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'SCALE_EXPLICIT_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if deleting then raise_application_error(-20863,'SCALE_DEVICE_DEACTIVATE_REQUIRED');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')is null or sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION')!='warehouse_settings_edit'
  or actor_value is null or :new.CHANGED_BY!=actor_value then raise_application_error(-20882,'WAREHOUSE_SCALE_CONFIGURATION_ACTOR_REQUIRED');end if;
 if updating then v_old_ware:=:old.WARE_ID;else v_old_ware:=:new.WARE_ID;end if;
 select count(*)into n from RUSERS where ID=actor_value and nvl(DELETED,0)=0
  and(upper(trim(USER_GROUP))='GLOBAL_ADMIN'or(WARE_ID=:new.WARE_ID and WARE_ID=v_old_ware));
 if n!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_CURRENT_CONFIGURATION_WARE_REQUIRED');end if;
 RRL_STOCK_MATH.assert_base(:new.CAPACITY_KG,9);RRL_STOCK_MATH.assert_base(:new.RESOLUTION_KG,9);
 if :new.RESOLUTION_KG>:new.CAPACITY_KG then raise_application_error(-20863,'SCALE_RESOLUTION_CAPACITY_INVALID');end if;
 select count(*)into n from RRL_CELLS where CELL=:new.POST_CELL and WARE_ID=:new.WARE_ID;
 if n!=1 then raise_application_error(-20886,'WAREHOUSE_SCALE_UNIQUE_POST_CELL_REQUIRED');end if;
 select count(*)into n from RUSERS where ID=:new.SENDER_ID and nvl(DELETED,0)=0 and WARE_ID=:new.WARE_ID
  and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
 if n!=1 then raise_application_error(-20882,'WAREHOUSE_SCALE_DEDICATED_SENDER_REQUIRED');end if;
 if inserting and :new.POLICY_VERSION!=1 then raise_application_error(-20863,'SCALE_INITIAL_VERSION_REQUIRED');end if;
 if updating and(:new.DEVICE_ID!=:old.DEVICE_ID or :new.POLICY_VERSION!=:old.POLICY_VERSION+1)then raise_application_error(-20863,'SCALE_DEVICE_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_WH_SCALE_CAPTURE_GUARD before insert or update or delete on RRL_WH_SCALE_CAPTURE for each row
begin
 if not inserting then raise_application_error(-20863,'SCALE_ORIGINAL_CAPTURE_IMMUTABLE');end if;
 if sys_context('RRL_WH_SCALE_CTX','TX_ID')is null or sys_context('RRL_WH_SCALE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_WH_SCALE_CTX','CAPTURE_KEY')is null or sys_context('RRL_WH_SCALE_CTX','CAPTURE_KEY')!=:new.CAPTURE_KEY then raise_application_error(-20863,'SCALE_CAPTURE_PACKAGE_REQUIRED');end if;
end;
/
