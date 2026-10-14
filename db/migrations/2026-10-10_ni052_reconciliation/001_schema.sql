declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_TT_LOAD_RECONCILE';
 if n=0 then execute immediate q'[create table RRL_TT_LOAD_RECONCILE(
  LOAD_OPERATION_ID varchar2(100) primary key references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
  SHIPPING_OPERATION_ID varchar2(100) not null unique references RRL_STOCK_OPERATION(OPERATION_ID),
  RECONCILED_BY varchar2(50) not null,
  RECONCILED_AT timestamp with time zone default systimestamp not null)]';end if;
end;
/
