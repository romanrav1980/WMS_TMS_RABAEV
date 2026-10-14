create table RRL_STORE_LOAD_CUSTODY(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 RELEASED_AT timestamp with time zone not null,
 RELEASED_BY nvarchar2(50)not null
);
