begin execute immediate q'[create table RRL_TARE_RESOLUTION(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RESOLUTION_KIND varchar2(12) not null check(RESOLUTION_KIND in('DAMAGE','WRITE_OFF')),
 OWNER_WARE_ID number not null,PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 CUSTODIAN_KIND varchar2(12) not null check(CUSTODIAN_KIND in('WAREHOUSE','VEHICLE','STORE')),
 CUSTODIAN_ID varchar2(255 byte) not null,
 FROM_BALANCE_KEY raw(32) not null references RRL_TARE_BALANCE(BALANCE_KEY),
 TO_BALANCE_KEY raw(32),
 QUANTITY number(18,0) not null check(QUANTITY>0),
 DELIVERY_ACCEPT_OPERATION_ID varchar2(100) references RRL_TARE_ACCEPT(OPERATION_ID),
 DAMAGE_OPERATION_ID varchar2(100) references RRL_TARE_RESOLUTION(OPERATION_ID),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 check((RESOLUTION_KIND='DAMAGE' and TO_BALANCE_KEY is not null and DAMAGE_OPERATION_ID is null)or(RESOLUTION_KIND='WRITE_OFF' and TO_BALANCE_KEY is null and DAMAGE_OPERATION_ID is not null)),
 check(CUSTODIAN_KIND!='STORE' or DELIVERY_ACCEPT_OPERATION_ID is not null)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_RESOLUTION_DAMAGE_IX on RRL_TARE_RESOLUTION(DAMAGE_OPERATION_ID,RESOLUTION_KIND)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TARE_RESOLUTION_LOAN_IX on RRL_TARE_RESOLUTION(DELIVERY_ACCEPT_OPERATION_ID,RESOLUTION_KIND)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
