prompt [migration 2026-05-17-017] smoke cleanup

delete from RRL_PICK_DECISION_LOG
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_017');

delete from RRL_PICK_SHORTAGE
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_017');

delete from RRL_PICK_RESERVATION
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_017');

delete from RRL_PICK_TASK
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_017');

delete from RRL_PICK_PLAN_LINE
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_017');

delete from RRL_PICK_PLAN
 where CREATED_BY = 'SMOKE_017';

delete from RRL_CUSTOMER_ORDER_FULFILLMENT
 where CUSTOMER_ORDER_ID in (select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_017');

delete from RRL_CUSTOMER_ORDER_ROW
 where CUSTOMER_ORDER_ID in (select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_017');

delete from RRL_CUSTOMER_ORDER
 where CREATED_BY = 'SMOKE_017';

delete from RRL_CUSTOMER_STORE_MAP
 where CREATED_BY = 'SMOKE_017'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER_ADDRESS
 where CREATED_BY = 'SMOKE_017'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER
 where CREATED_BY = 'SMOKE_017'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_PICK_FACE_ARTICUL
 where CREATED_BY = 'SMOKE_017';

delete from RRL_PICK_FACE
 where CREATED_BY = 'SMOKE_017';

delete from RRL_PICK_ROUTE_CELL
 where CREATED_BY = 'SMOKE_017';

delete from RRL_PICK_ROUTE
 where CREATED_BY = 'SMOKE_017';

commit;

select 'SMOKE_017_PICK_PLANS' CHECK_NAME,
       count(*) CNT
  from RRL_PICK_PLAN
 where CREATED_BY = 'SMOKE_017';

select 'SMOKE_017_PICK_FACES' CHECK_NAME,
       count(*) CNT
  from RRL_PICK_FACE
 where CREATED_BY = 'SMOKE_017';

prompt [migration 2026-05-17-017] smoke cleanup done
