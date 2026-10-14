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
 where r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and p.SOURCE_ST_ID=:new.SOURCE_ST_ID and p.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and p.TARGET_TT_ID=:new.TARGET_TT_ID and ((:new.FINAL_ADDRESS_SOURCE='FROZEN_LOAD'and member.DESTINATION_ADDR=:new.FINAL_ADDRESS)or(:new.FINAL_ADDRESS_SOURCE='CURRENT_GUARDED_LEGACY'and member.DESTINATION_ADDR is null and json_value(:new.RESULT_JSON,'$.legacy_address_confirmed')='true'and exists(select 1 from RRL_SBORKA_PALLETS original where original.ID=p.SOURCE_ST_ID and original.ADDR=:new.FINAL_ADDRESS))) and x.TARGET_CELL=:new.SOURCE_CELL and stock.STOCK_VERSION=:new.STOCK_VERSION and stock.REMAIN=r.BASE_QTY and stock.HARD_RESERVED_BASE=0 and stock.BASE_UOM=r.BASE_UOM;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_ORIGINAL_PLACED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS s where s.ID=:new.ST_ID and s.PALLET_UID=:new.ST_IDENTIFIER and s.WARE_ID=:new.WARE_ID and s.RETURN_SUPPLIER_ID is null and s.ADDR=:new.FINAL_ADDRESS and nvl(s.CONDITION,0)<2 and s.TRANSTASK_ID is null;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_EXISTING_CONSTRUCTOR_REQUIRED');end if;
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_FACT_GUARD before insert or update or delete on RRL_INTERWARE_ONWARD_DISPATCH for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_ONWARD_FACT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_ONWARD_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='LOAD_SHIPMENT'and STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and json_value(RESOLVED_PLAN_JSON,'$.domain.shipment.domain.interwarehouse_onward_source.binding_operation_id')=:new.BIND_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'INTERWARE_ONWARD_ORIGINAL_LOADING_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_ONWARD_DISPATCH',op));
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_ST_GUARD before update or delete on RRL_SBORKA_PALLETS for each row
declare n number;t number;
begin
 select count(*),max(TARGET_TT_ID)into n,t from RRL_INTERWARE_ONWARD_BIND where ST_ID=:old.ID;if n=0 then return;end if;
 if deleting then raise_application_error(-20863,'INTERWARE_ONWARD_ST_PRESERVE');end if;
 if :new.ID!=:old.ID or :new.PALLET_UID!=:old.PALLET_UID or :new.WARE_ID!=:old.WARE_ID or :new.ADDR!=:old.ADDR or nvl(:new.ST_NUMBER,chr(0))!=nvl(:old.ST_NUMBER,chr(0))or :new.RETURN_SUPPLIER_ID is not null then raise_application_error(-20863,'INTERWARE_ONWARD_ST_SOURCE_IMMUTABLE');end if;
 if :new.TRANSTASK_ID is not null and :new.TRANSTASK_ID!=t then raise_application_error(-20886,'INTERWARE_ONWARD_ONLY_ORIGINAL_TARGET_TRIP');end if;
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_ROW_GUARD before insert or update of PALLET_UID,ARTICUL,QUANTITY,EI or delete on RRL_SBORKA_PALLET_ROWS for each row
declare n number;
begin
 select count(*)into n from RRL_INTERWARE_ONWARD_BIND where ST_IDENTIFIER in(:old.PALLET_UID,:new.PALLET_UID);if n=0 then return;end if;
 if inserting or deleting then raise_application_error(-20863,'INTERWARE_ONWARD_ST_ROWS_IMMUTABLE');end if;
 if nvl(:new.PALLET_UID,chr(0))!=nvl(:old.PALLET_UID,chr(0))or nvl(:new.ARTICUL,chr(0))!=nvl(:old.ARTICUL,chr(0))or nvl(:new.QUANTITY,-1)!=nvl(:old.QUANTITY,-1)or nvl(:new.EI,chr(0))!=nvl(:old.EI,chr(0))then raise_application_error(-20863,'INTERWARE_ONWARD_ST_ROWS_IMMUTABLE');end if;
end;
/
