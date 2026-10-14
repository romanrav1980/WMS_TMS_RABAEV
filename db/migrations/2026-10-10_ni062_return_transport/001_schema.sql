begin execute immediate q'[create table RRL_STORE_RETURN_TRANSPORT(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 APPROVAL_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_APPROVAL(OPERATION_ID),
 SAP_OPERATION_ID varchar2(100 byte) not null references RRL_STORE_RETURN_SAP(OPERATION_ID),
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 VEHICLE_ID number not null references RRL_TR_VEHICLE(ID),
 VEHICLE_NUMBER varchar2(50 byte) not null,
 DRIVER_ID number not null,
 STORE_ADDR varchar2(255 byte) not null,
 RECEIVING_WARE_ID number not null,
 GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
 PHYSICAL_PLACES number(10) not null check(PHYSICAL_PLACES>0 and PHYSICAL_PLACES=trunc(PHYSICAL_PLACES)),
 CAPACITY_BASIS varchar2(30 byte) default 'CONSERVATIVE_FULL_OUTBOUND' not null,
 PLANNED_BY nvarchar2(50) not null,
 PLANNED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_STORE_RETURN_TRIP_IDX on RRL_STORE_RETURN_TRANSPORT(TT_ID,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
