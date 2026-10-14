create or replace trigger RRL_INTERWARE_ONWARD_BIND_GUARD before insert or update or delete on RRL_INTERWARE_ONWARD_BIND for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_ONWARD_BIND_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_ONWARD_METADATA_ACTOR_REQUIRED');end if;
 select count(*)into n from RUSERS u where ID=:new.ACTOR and nvl(DELETED,0)=0 and(WARE_ID=:new.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'outgoing_pallet_edit')=1 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_ONWARD_WARE_DISPATCHER_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID join RRL_INTERWARE_PLACEMENT x on x.RECEIPT_OPERATION_ID=r.OPERATION_ID join RRL_INTERWARE_CUSTODY_PROOF c on c.RECEIPT_OPERATION_ID=r.OPERATION_ID
 join RRL_REMAINS stock on stock.UID_POLETA=r.ROOT_UID and stock.CELL=x.TARGET_CELL
 join RRL_TT_HU_LOAD_ST member on member.LOAD_OPERATION_ID=p.SOURCE_LOAD_OPERATION_ID and member.SBORKA_PALLET_ID=p.SOURCE_ST_ID
 where r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and p.SOURCE_ST_ID=:new.SOURCE_ST_ID and p.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and RRL_INTERWARE_ROUTING.target_trip(p.OPERATION_ID)=:new.TARGET_TT_ID and ((:new.FINAL_ADDRESS_SOURCE='FROZEN_LOAD'and member.DESTINATION_ADDR=:new.FINAL_ADDRESS)or(:new.FINAL_ADDRESS_SOURCE='CURRENT_GUARDED_LEGACY'and member.DESTINATION_ADDR is null and json_value(:new.RESULT_JSON,'$.legacy_address_confirmed')='true'and exists(select 1 from RRL_SBORKA_PALLETS original where original.ID=p.SOURCE_ST_ID and original.ADDR=:new.FINAL_ADDRESS))) and x.TARGET_CELL=:new.SOURCE_CELL and stock.STOCK_VERSION=:new.STOCK_VERSION and stock.REMAIN=r.BASE_QTY and stock.HARD_RESERVED_BASE=0 and stock.BASE_UOM=r.BASE_UOM;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_ORIGINAL_PLACED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS s where s.ID=:new.ST_ID and s.PALLET_UID=:new.ST_IDENTIFIER and s.WARE_ID=:new.WARE_ID and s.RETURN_SUPPLIER_ID is null and s.ADDR=:new.FINAL_ADDRESS and nvl(s.CONDITION,0)<2 and s.TRANSTASK_ID is null;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_EXISTING_CONSTRUCTOR_REQUIRED');end if;
end;
/
