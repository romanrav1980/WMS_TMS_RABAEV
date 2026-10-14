create or replace trigger RRL_IW_REC_ST_INSERT_GUARD before insert on RRL_IW_RECOVERY_ST_BIND for each row
declare n number;owners clob;
begin
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
 select count(*)into n from RUSERS u where u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 and(u.WARE_ID=:new.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1 and RRL_HAS_WRIGHT(u.ID,'outgoing_pallet_edit')=1;
 if n!=1 then raise_application_error(-20882,'RECOVERY_BIND_CURRENT_WARE_ACTOR_REQUIRED');end if;
 select original.ORIGINAL_FULFILLMENT_JSON into owners
 from RRL_INTERWARE_RECOVERY_RECEIPT r join RRL_INTERWARE_SHORTAGE_FACT loss on loss.OPERATION_ID=r.LOSS_OPERATION_ID
 join RRL_INTERWARE_ONWARD_BIND original on original.RECEIPT_OPERATION_ID=loss.RECEIPT_OPERATION_ID
 join RRL_IW_RECOVERY_PLACEMENT placed on placed.RECOVERY_OPERATION_ID=r.OPERATION_ID
 join RRL_REMAINS stock on stock.UID_POLETA=r.ROOT_UID and stock.CELL=placed.TARGET_CELL
 join RRL_STOCK_OPERATION recovered on recovered.OPERATION_ID=r.OPERATION_ID and recovered.STATE='APPLIED'and recovered.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'
 where r.OPERATION_ID=:new.RECOVERY_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID
 and original.RECEIPT_OPERATION_ID=:new.RECEIPT_OPERATION_ID and original.SOURCE_ST_ID=:new.SOURCE_ST_ID
 and original.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and original.FINAL_ADDRESS=:new.FINAL_ADDRESS
 and original.FINAL_ADDRESS_SOURCE=:new.FINAL_ADDRESS_SOURCE and placed.TARGET_CELL=:new.SOURCE_CELL
 and stock.REMAIN=r.BASE_QTY and stock.HARD_RESERVED_BASE=0 and stock.BASE_UOM=r.BASE_UOM and stock.STOCK_VERSION=:new.STOCK_VERSION;
 if dbms_lob.compare(owners,:new.ORIGINAL_FULFILLMENT_JSON)!=0 then raise_application_error(-20886,'RECOVERY_BIND_ORIGINAL_OWNER_CHANGED');end if;
 exception when no_data_found then raise_application_error(-20886,'RECOVERY_BIND_ORIGINAL_PLACED_SOURCE_REQUIRED');
end;
/
