create or replace trigger RRL_IW_GROUP_ONWARD_GUARD before insert or update or delete on RRL_IW_GROUP_ONWARD for each row
declare n number;ware number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_ONWARD_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select WARE_ID into ware from RRL_IW_GROUP_RECEIPT where OPERATION_ID=:new.RECEIPT_OPERATION_ID;
 select count(*)into n from RUSERS where ID=:new.ACTOR and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1 and RRL_HAS_WRIGHT(ID,'outgoing_pallet_edit')=1 and(WARE_ID=ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_ONWARD_CURRENT_DISPATCHER_REQUIRED');end if;
 select count(*)into n from RRL_IW_GROUP_PLACEMENT p join RRL_IW_GROUP_CUSTODY c on c.RECEIPT_OPERATION_ID=p.RECEIPT_OPERATION_ID where p.RECEIPT_OPERATION_ID=:new.RECEIPT_OPERATION_ID;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_PLACEMENT_CUSTODY_REQUIRED');end if;
end;
/
create or replace trigger RRL_IW_GROUP_ST_BIND_GUARD before insert or update or delete on RRL_IW_GROUP_ST_BIND for each row
declare n number;wire clob;expected number;matched number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_BIND_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_IW_GROUP_ONWARD h join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=h.RECEIPT_OPERATION_ID
 join RRL_IW_GROUP_RECEIPT_LINE l on l.OPERATION_ID=r.OPERATION_ID and l.ROOT_UID=:new.ROOT_UID and l.ST_ID=:new.SOURCE_ST_ID
 join RRL_IW_GROUP_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID and p.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and p.TARGET_TT_ID=:new.TARGET_TT_ID
 join RRL_IW_GROUP_PLACEMENT placed on placed.RECEIPT_OPERATION_ID=r.OPERATION_ID and placed.TARGET_CELL=:new.SOURCE_CELL
 join RRL_IW_GROUP_CUSTODY c on c.RECEIPT_OPERATION_ID=r.OPERATION_ID
 join RRL_REMAINS stock on stock.UID_POLETA=l.ROOT_UID and stock.CELL=:new.SOURCE_CELL and stock.REMAIN=l.BASE_QTY and stock.BASE_UOM=l.BASE_UOM and stock.HARD_RESERVED_BASE=0 and stock.STOCK_VERSION=:new.STOCK_VERSION
 join RRL_SBORKA_PALLETS st on st.ID=:new.ST_ID and st.PALLET_UID=:new.ST_IDENTIFIER and st.WARE_ID=r.WARE_ID and st.ADDR=:new.FINAL_ADDRESS and st.RETURN_SUPPLIER_ID is null
 join RRL_TT_HU_LOAD_ST source on source.LOAD_OPERATION_ID=p.SOURCE_LOAD_OPERATION_ID and source.SBORKA_PALLET_ID=l.ST_ID and source.DESTINATION_ADDR=st.ADDR
 where h.OPERATION_ID=:new.ONWARD_OPERATION_ID and h.RECEIPT_OPERATION_ID=:new.RECEIPT_OPERATION_ID and h.ACTOR=:new.ACTOR and r.WARE_ID=:new.WARE_ID;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_NATIVE_BIND_SOURCE_REQUIRED');end if;
 select count(*)into expected from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:new.SOURCE_ST_ID and STATUS='SHIPPED';
 select count(*)into matched from RRL_CUSTOMER_ORDER_FULFILLMENT f join json_table(:new.ORIGINAL_FULFILLMENT_JSON,'$[*]'columns(F_ID number path '$.fulfillment_id',O_ID number path '$.customer_order_id',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',S varchar2(20)path '$.status'))proof
 on proof.F_ID=f.FULFILLMENT_ID and proof.O_ID=f.CUSTOMER_ORDER_ID and RRL_STOCK_MATH.quantity(proof.Q)=f.FACT_QTY and proof.B=f.FACT_UOM and proof.S=f.STATUS
 where f.LEGACY_SBORKA_PALLET_ID=:new.SOURCE_ST_ID and f.STATUS='SHIPPED';
 if expected!=matched then raise_application_error(-20886,'INTERWARE_GROUP_ORIGINAL_FULFILLMENT_REQUIRED');end if;
end;
/
create or replace trigger RRL_IW_GROUP_DISPATCH_GUARD before insert or update or delete on RRL_IW_GROUP_DISPATCH for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;wire clob;kind_value varchar2(80);state_value varchar2(20);
begin
 if not inserting or op is null or op!=:new.OPERATION_ID or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_DISPATCH_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 select count(*)into n from json_table(wire,'$.domain.shipments[*]'columns(BIND_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',R_ID varchar2(100)path '$.domain.interwarehouse_onward_source.group_receipt_operation_id',S_ID number path '$.domain.interwarehouse_onward_source.st_id',U varchar2(200)path '$.domain.interwarehouse_onward_source.uid',Q varchar2(60)path '$.domain.interwarehouse_onward_source.quantity',B varchar2(20)path '$.domain.interwarehouse_onward_source.base_uom'))proof
 join RRL_IW_GROUP_ST_BIND bind on bind.OPERATION_ID=proof.BIND_ID and bind.ST_ID=proof.S_ID and bind.RECEIPT_OPERATION_ID=proof.R_ID and bind.ROOT_UID=proof.U
 where proof.BIND_ID=:new.BIND_OPERATION_ID and proof.R_ID=:new.RECEIPT_OPERATION_ID and proof.S_ID=:new.ST_ID and proof.U=:new.ROOT_UID and RRL_STOCK_MATH.quantity(proof.Q)=:new.BASE_QTY and proof.B=:new.BASE_UOM and bind.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID;
 if kind_value!='HU_SHIP'or state_value!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_RESOLVED_DISPATCH_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_DISPATCH',op));
end;
/
