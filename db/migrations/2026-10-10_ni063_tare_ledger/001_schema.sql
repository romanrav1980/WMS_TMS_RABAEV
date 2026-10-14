begin execute immediate q'[create table RRL_TARE_BALANCE(
 BALANCE_KEY raw(32) primary key,
 OWNER_WARE_ID number not null,
 PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 CONDITION_CODE varchar2(10) not null check(CONDITION_CODE in('GOOD','DAMAGED')),
 CUSTODIAN_KIND varchar2(12) not null check(CUSTODIAN_KIND in('WAREHOUSE','VEHICLE','STORE')),
 CUSTODIAN_ID varchar2(255 byte) not null,
 QUANTITY number(18,0) default 0 not null check(QUANTITY>=0),
 BALANCE_VERSION number(19,0) default 1 not null check(BALANCE_VERSION>=1),
 LAST_OPERATION_ID varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
 UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TARE_BALANCE_UQ unique(OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_OFFER(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 FROM_BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 TO_BALANCE_KEY raw(32) not null,
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 VEHICLE_ID number not null references RRL_TR_VEHICLE(ID),
 VEHICLE_NUMBER varchar2(50) not null,
 STORE_ADDR varchar2(255 byte),
 OWNER_WARE_ID number not null,
 PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 CONDITION_CODE varchar2(10) not null,
 FROM_KIND varchar2(12) not null,FROM_ID varchar2(255 byte) not null,
 TO_KIND varchar2(12) not null,TO_ID varchar2(255 byte) not null,
 QUANTITY number(18,0) not null check(QUANTITY>0),
 OFFERED_BY nvarchar2(50) not null,
 OFFERED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_ACCEPT(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 OFFER_OPERATION_ID varchar2(100) not null unique references RRL_TARE_OFFER(OPERATION_ID),
 ACCEPTED_QTY number(18,0) not null check(ACCEPTED_QTY>0),
 SHORT_QTY number(18,0) not null check(SHORT_QTY>=0),
 ACCEPTED_BY nvarchar2(50) not null,
 ACCEPTED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TARE_JOURNAL(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 ACTION_KIND varchar2(12) not null check(ACTION_KIND in('COUNT','TRANSFER')),
 FROM_BALANCE_KEY raw(32),TO_BALANCE_KEY raw(32) not null,
 QUANTITY number(18,0) not null,
 BEFORE_QTY number(18,0),AFTER_QTY number(18,0),
 REASON_TEXT varchar2(2000 byte),DECISION_REFERENCE varchar2(255 byte),
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 check((ACTION_KIND='COUNT' and BEFORE_QTY is not null and AFTER_QTY is not null and REASON_TEXT is not null and DECISION_REFERENCE is not null) or(ACTION_KIND='TRANSFER' and FROM_BALANCE_KEY is not null and QUANTITY>0))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_OFFER_TRIP_IX on RRL_TARE_OFFER(TT_ID,OFFERED_AT)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_BALANCE_HOLDER_IX on RRL_TARE_BALANCE(CUSTODIAN_KIND,CUSTODIAN_ID,CONDITION_CODE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
