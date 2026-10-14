begin execute immediate 'alter table RRL_TT_HU_LOAD_FACT add(CUSTODY_RELEASED_AT timestamp with time zone,CUSTODY_RELEASE_OPERATION_ID varchar2(100)references RRL_STOCK_OPERATION(OPERATION_ID))';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate q'[create table RRL_INTERWARE_CUSTODY_PROOF(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
