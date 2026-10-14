begin execute immediate q'[create table RRL_STORE_RETURN_WARE_POLICY(
 WARE_ID number primary key,
 SUPPLIER_RECEIVE_CELL varchar2(60 byte) not null,
 DISPOSAL_RECEIVE_CELL varchar2(60 byte) not null,
 POLICY_VERSION number(19) default 1 not null check(POLICY_VERSION>0),
 CHANGED_BY nvarchar2(50) not null,
 CHANGED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_RECEIPT(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 PICKUP_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_PICKUP(OPERATION_ID),
 APPROVAL_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_APPROVAL(OPERATION_ID),
 SAP_OPERATION_ID varchar2(100 byte) not null references RRL_STORE_RETURN_SAP(OPERATION_ID),
 UID_PALLET varchar2(200 byte) not null unique references RRL_PALLETS(UID_PALLET),
 ORIGINAL_LOT_UID varchar2(200 byte) not null,
 WARE_ID number not null,
 RECEIVE_CELL varchar2(60 byte) not null,
 ARTICLE varchar2(160 byte) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),
 BASE_UOM varchar2(20 byte) not null,
 DISPOSITION varchar2(20 byte) not null check(DISPOSITION in('SUPPLIER','DISPOSAL')),
 OBSERVED_BATCH varchar2(100 byte) not null,
 BATCH_SOURCE varchar2(30 byte) not null check(BATCH_SOURCE in('ORIGINAL_SAP_VERIFIED','OBSERVED_LEGACY_UNVERIFIED')),
 EXPIRY_DATE date not null,
 GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
 NET_WEIGHT_KG number(27,9) not null check(NET_WEIGHT_KG>0),
 STOCK_EVENT_ID number not null,
 RECEIVED_BY nvarchar2(50) not null,
 RECEIVED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_STORE_RETURN_WEIGHT_CHECK check(NET_WEIGHT_KG<=GROSS_WEIGHT_KG)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_STORE_RETURN_RECEIPT_WARE on RRL_STORE_RETURN_RECEIPT(WARE_ID,RECEIVED_AT,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
