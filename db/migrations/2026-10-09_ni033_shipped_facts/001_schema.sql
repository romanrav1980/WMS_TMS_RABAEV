declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_ORDER_FULFILLMENT' and COLUMN_NAME='SHIPPED_OPERATION_ID';
 if n=0 then execute immediate 'alter table RRL_CUSTOMER_ORDER_FULFILLMENT add(SHIPPED_OPERATION_ID varchar2(100),SHIPPED_AT timestamp)';end if;
end;
/
