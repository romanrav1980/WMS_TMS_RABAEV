prompt [migration 2026-05-17-014] smoke cleanup

delete from RRL_CUSTOMER_ORDER_FULFILLMENT
 where CUSTOMER_ORDER_ID in (
   select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_014'
 );

delete from RRL_CUSTOMER_ORDER_ROW
 where CUSTOMER_ORDER_ID in (
   select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_014'
 );

delete from RRL_CUSTOMER_ORDER
 where CREATED_BY = 'SMOKE_014';

delete from RRL_CUSTOMER_STORE_MAP
 where CREATED_BY = 'SMOKE_014'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER_ADDRESS
 where CREATED_BY = 'SMOKE_014'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER
 where CREATED_BY = 'SMOKE_014'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

commit;

select 'SMOKE_014_CUSTOMER_ORDER_ROWS' CHECK_NAME,
       count(*) CNT
  from RRL_CUSTOMER_ORDER
 where CREATED_BY = 'SMOKE_014';

prompt [migration 2026-05-17-014] smoke cleanup done
