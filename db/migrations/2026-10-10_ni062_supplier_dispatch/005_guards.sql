create or replace trigger RRL_SUP_RETURN_BIND_GUARD before insert or update or delete on RRL_STORE_RETURN_SUP_BIND for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_SOURCE_HISTORY_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if RRL_HAS_WRIGHT(:new.ACTOR,'store_return_approve')!=1 or RRL_HAS_WRIGHT(:new.ACTOR,'outgoing_pallet_edit')!=1 then raise_application_error(-20882,'SUP_RETURN_APPROVED_PREPARATION_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS where ID=:new.ST_ID and PALLET_UID=:new.ST_IDENTIFIER and RETURN_SUPPLIER_ID=:new.SUPPLIER_INN;
 if n!=1 then raise_application_error(-20886,'SUP_RETURN_EXISTING_ST_IDENTITY_REQUIRED');end if;
end;
/
create or replace trigger RRL_SUP_RETURN_DISPATCH_GUARD before insert or update or delete on RRL_STORE_RETURN_SUP_DISPATCH for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_DISPATCH_HISTORY_IMMUTABLE');end if;
 if op is null or :new.OPERATION_ID!=op or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'SUP_RETURN_DISPATCH_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='LOAD_SHIPMENT'or v_state!='IN_FLIGHT'then raise_application_error(-20863,'SUP_RETURN_ACTUAL_LOADING_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_SUP_DISPATCH',op));
end;
/

create or replace trigger RRL_SUP_RETURN_ST_SOURCE_GUARD before update of PALLET_UID,WARE_ID,RETURN_SUPPLIER_ID on RRL_SBORKA_PALLETS for each row
declare n number;
begin
 if nvl(:new.PALLET_UID,'~')=nvl(:old.PALLET_UID,'~')and nvl(:new.WARE_ID,-1)=nvl(:old.WARE_ID,-1)and nvl(:new.RETURN_SUPPLIER_ID,'~')=nvl(:old.RETURN_SUPPLIER_ID,'~')then return;end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_BIND where ST_ID=:old.ID;
 if n!=0 then raise_application_error(-20863,'SUP_RETURN_PREPARED_SOURCE_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_SUP_RETURN_ROWS_SOURCE_GUARD before insert or delete or update of PALLET_UID,ARTICUL,EI,QUANTITY on RRL_SBORKA_PALLET_ROWS for each row
declare n number;
begin
 if updating and nvl(:new.PALLET_UID,'~')=nvl(:old.PALLET_UID,'~')and nvl(:new.ARTICUL,'~')=nvl(:old.ARTICUL,'~')and nvl(:new.EI,'~')=nvl(:old.EI,'~')and nvl(:new.QUANTITY,-1)=nvl(:old.QUANTITY,-1)then return;end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_BIND where ST_IDENTIFIER=:new.PALLET_UID or ST_IDENTIFIER=:old.PALLET_UID;
 if n!=0 then raise_application_error(-20863,'SUP_RETURN_PREPARED_ROWS_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_STORE_SUPPLIER_CARGO_GUARD before insert on RRL_STORE_RECEIPT_FACT for each row
declare n number;
begin
 select count(*)into n from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS st on st.ID=m.SBORKA_PALLET_ID where m.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and st.RETURN_SUPPLIER_ID is not null;
 if n!=0 then raise_application_error(-20886,'STORE_RECEIPT_SUPPLIER_CARGO_NOT_ALLOWED');end if;
end;
/
