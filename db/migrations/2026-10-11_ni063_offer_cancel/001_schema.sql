create table RRL_TARE_OFFER_CANCEL(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 OFFER_OPERATION_ID varchar2(100)not null unique references RRL_TARE_OFFER(OPERATION_ID),
 REASON nvarchar2(500)not null,CANCELLED_BY nvarchar2(50)not null,
 CANCELLED_AT timestamp with time zone default systimestamp not null
);
