prompt [migration 2026-05-17-011] MES production completion - smoke cleanup

delete from RRL_REMAINS
 where UID_POLETA in ('MES-SMOKE-RAW-PALLET-011', 'MES-SMOKE-FG-PALLET-011');

delete from RRL_EVENTS
 where UID_POLETA in ('MES-SMOKE-RAW-PALLET-011', 'MES-SMOKE-FG-PALLET-011');

delete from RRL_PROD_BATCH_PALLETS
 where UID_PALLET in ('MES-SMOKE-RAW-PALLET-011', 'MES-SMOKE-FG-PALLET-011');

delete from RRL_PALLETS
 where UID_PALLET in ('MES-SMOKE-RAW-PALLET-011', 'MES-SMOKE-FG-PALLET-011');

delete from RRL_PROD_RAW_USAGE
 where PROD_BATCH_ID in (
   select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'MES-SMOKE-LOT-011'
 );

delete from RRL_TRACE_EDGE
 where FROM_ENTITY_ID in (
   select to_char(PRODUCTION_ORDER_ID)
     from RRL_PRODUCTION_ORDER
    where ORDER_NO = 'MES-SMOKE-ORDER-011'
 )
 or TO_ENTITY_ID in (
   select to_char(PROD_BATCH_ID)
     from RRL_PROD_BATCH
    where PROD_BATCH_NO = 'MES-SMOKE-LOT-011'
 );

delete from RRL_TRACE_EVENT
 where IDEMPOTENCY_KEY in ('MES-SMOKE-COMPLETE-011', 'MES-SMOKE-ORDER-011:TRACE');

delete from RRL_EVENT_OUTBOX
 where IDEMPOTENCY_KEY in ('MES-SMOKE-COMPLETE-011', 'MES-SMOKE-ORDER-011:OUTBOX');

delete from RRL_MES_COMPLETION
 where IDEMPOTENCY_KEY = 'MES-SMOKE-COMPLETE-011';

delete from RRL_MES_MOVEMENT
 where PRODUCTION_ORDER_ID in (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO = 'MES-SMOKE-ORDER-011'
 );

delete from RRL_PROD_ORDER_BOM_LINE
 where PRODUCTION_ORDER_ID in (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO = 'MES-SMOKE-ORDER-011'
 );

delete from RRL_PRODUCTION_ORDER
 where ORDER_NO = 'MES-SMOKE-ORDER-011';

delete from RRL_PROD_BATCH
 where PROD_BATCH_NO = 'MES-SMOKE-LOT-011';

delete from RRL_BOM_AUDIT
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE = 'MES-SMOKE-BOM-011');

delete from RRL_BOM_LINE
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE = 'MES-SMOKE-BOM-011');

delete from RRL_BOM
 where BOM_CODE = 'MES-SMOKE-BOM-011';

commit;

prompt [migration 2026-05-17-011] smoke cleanup done
