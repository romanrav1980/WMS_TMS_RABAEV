declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_ORDER_FULFILLMENT' and COLUMN_NAME='PICKED_PALLET_UID';
 if n=0 then execute immediate 'alter table RRL_CUSTOMER_ORDER_FULFILLMENT add (PICKED_WAREHOUSE_TASK_ID number,PICKED_OPERATION_ID varchar2(100),PICKED_PALLET_UID varchar2(150),PICKED_STOCK_VERSION number)';end if;
end;
/
