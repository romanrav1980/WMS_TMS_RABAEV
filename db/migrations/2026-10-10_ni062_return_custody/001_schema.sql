begin execute immediate q'[create table RRL_TRANSPORT_DRIVER_USER(
 DRIVER_ID number primary key,
 USER_ID nvarchar2(50) not null unique,
 ACTIVE number(1) default 0 not null check(ACTIVE in(0,1)),
 BINDING_VERSION number(19) default 1 not null check(BINDING_VERSION>0),
 CHANGED_BY nvarchar2(50) not null,
 CHANGED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_HANDOVER(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 TRANSPORT_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_TRANSPORT(OPERATION_ID),
 PALLET_IDENTIFIER varchar2(200 byte) not null,
 GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
 PHYSICAL_PLACES number(10) not null check(PHYSICAL_PLACES>0 and PHYSICAL_PLACES=trunc(PHYSICAL_PLACES)),
 HANDED_BY nvarchar2(50) not null,
 HANDED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_PICKUP(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 HANDOVER_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_HANDOVER(OPERATION_ID),
 DRIVER_ID number not null,
 VEHICLE_ID number not null references RRL_TR_VEHICLE(ID),
 VEHICLE_NUMBER varchar2(50 byte) not null,
 BINDING_VERSION number(19) not null,
 TAKEN_BY nvarchar2(50) not null,
 TAKEN_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
