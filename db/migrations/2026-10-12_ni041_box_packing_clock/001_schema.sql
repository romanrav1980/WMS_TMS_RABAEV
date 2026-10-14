begin execute immediate q'[create table RRL_HU_PACK_CYCLE(
 PARENT_UID varchar2(200)not null references RRL_PALLETS(UID_PALLET),
 START_CONTENT_VERSION number(19)not null check(START_CONTENT_VERSION>0),
 START_OPERATION_ID varchar2(100)not null references RRL_STOCK_OPERATION(OPERATION_ID),
 WARE_ID number not null,ACTOR nvarchar2(50)not null,
 STARTED_AT_INSTANT timestamp with time zone not null,
 primary key(PARENT_UID,START_CONTENT_VERSION),unique(PARENT_UID,START_OPERATION_ID))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
