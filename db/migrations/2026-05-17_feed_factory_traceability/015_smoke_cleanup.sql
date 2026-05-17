prompt [migration 2026-05-17-015] smoke cleanup

delete from RRL_SHIPMENT_PART
 where CREATED_BY = 'SMOKE_015';

delete from RRL_CUSTOMER_VEHICLE_RULE
 where CREATED_BY = 'SMOKE_015';

delete from RRL_CUSTOMER_PRODUCT_STACK_RULE
 where CREATED_BY = 'SMOKE_015';

delete from RRL_CUSTOMER_SHELF_LIFE_RULE
 where CREATED_BY = 'SMOKE_015';

delete from RRL_CUSTOMER_ORDER_FULFILLMENT
 where CUSTOMER_ORDER_ID in (
   select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_015'
 );

delete from RRL_CUSTOMER_ORDER_ROW
 where CUSTOMER_ORDER_ID in (
   select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_015'
 );

delete from RRL_CUSTOMER_ORDER
 where CREATED_BY = 'SMOKE_015';

delete from RRL_CUSTOMER_STORE_MAP
 where CREATED_BY = 'SMOKE_015'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER_ADDRESS
 where CREATED_BY = 'SMOKE_015'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER
 where CREATED_BY = 'SMOKE_015'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

commit;

select 'SMOKE_015_SHIPMENT_PARTS' CHECK_NAME,
       count(*) CNT
  from RRL_SHIPMENT_PART
 where CREATED_BY = 'SMOKE_015';

prompt [migration 2026-05-17-015] smoke cleanup done
