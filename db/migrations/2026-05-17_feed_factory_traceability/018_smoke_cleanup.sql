prompt [migration 2026-05-17-018] smoke cleanup

delete from RRL_PICK_WAVE_AUDIT
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_TASK
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_REPLENISH_TASK
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_RESERVATION
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_SHORTAGE
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_DEMAND
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_LINE
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE_ORDER
 where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_WAVE
 where CREATED_BY = 'SMOKE_018';

delete from RRL_PICK_DECISION_LOG
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_SHORTAGE
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_RESERVATION
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_TASK
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_PLAN_LINE
 where PICK_PLAN_ID in (select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY = 'SMOKE_018');

delete from RRL_PICK_PLAN
 where CREATED_BY = 'SMOKE_018';

delete from RRL_CUSTOMER_ORDER_FULFILLMENT
 where CUSTOMER_ORDER_ID in (select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_018');

delete from RRL_CUSTOMER_ORDER_ROW
 where CUSTOMER_ORDER_ID in (select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY = 'SMOKE_018');

delete from RRL_CUSTOMER_ORDER
 where CREATED_BY = 'SMOKE_018';

delete from RRL_CUSTOMER_STORE_MAP
 where CREATED_BY = 'SMOKE_018'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER_ADDRESS
 where CREATED_BY = 'SMOKE_018'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

delete from RRL_CUSTOMER
 where CREATED_BY = 'SMOKE_018'
   and CUSTOMER_ID not in (select CUSTOMER_ID from RRL_CUSTOMER_ORDER);

commit;

select 'SMOKE_018_PICK_WAVES' CHECK_NAME,
       count(*) CNT
  from RRL_PICK_WAVE
 where CREATED_BY = 'SMOKE_018';

select 'SMOKE_018_PICK_PLANS' CHECK_NAME,
       count(*) CNT
  from RRL_PICK_PLAN
 where CREATED_BY = 'SMOKE_018';

prompt [migration 2026-05-17-018] smoke cleanup done
