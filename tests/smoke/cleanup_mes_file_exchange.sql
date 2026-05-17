prompt [smoke] cleanup MES file exchange workflow

delete from RRL_REMAINS
 where UID_POLETA like 'FILE-MES-RAW-%'
    or UID_POLETA like 'FILE-MES-FG-%';

delete from RRL_EVENTS
 where UID_POLETA like 'FILE-MES-RAW-%'
    or UID_POLETA like 'FILE-MES-FG-%';

delete from RRL_PROD_BATCH_PALLETS
 where UID_PALLET like 'FILE-MES-RAW-%'
    or UID_PALLET like 'FILE-MES-FG-%';

delete from RRL_PALLETS
 where UID_PALLET like 'FILE-MES-RAW-%'
    or UID_PALLET like 'FILE-MES-FG-%';

delete from RRL_FILE_EXCHANGE_LOG
 where MESSAGE_ID like 'FILE-MES-%';

delete from RRL_PROD_RAW_USAGE
 where PRODUCTION_ORDER_ID in (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO like 'FILE-MES-ORDER-%'
 );

delete from RRL_TRACE_EDGE
 where FROM_ENTITY_ID in (
   select to_char(PRODUCTION_ORDER_ID)
     from RRL_PRODUCTION_ORDER
    where ORDER_NO like 'FILE-MES-ORDER-%'
 )
 or TO_ENTITY_ID in (
   select to_char(PROD_BATCH_ID)
     from RRL_PROD_BATCH
    where PROD_BATCH_NO like 'FILE-MES-LOT-%'
 );

delete from RRL_TRACE_EVENT
 where IDEMPOTENCY_KEY like 'FILE-MES-%';

delete from RRL_EVENT_OUTBOX
 where IDEMPOTENCY_KEY like 'FILE-MES-%';

delete from RRL_MES_COMPLETION
 where IDEMPOTENCY_KEY like 'FILE-MES-%';

delete from RRL_MES_MOVEMENT
 where PRODUCTION_ORDER_ID in (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO like 'FILE-MES-ORDER-%'
 );

delete from RRL_PROD_ORDER_BOM_LINE
 where PRODUCTION_ORDER_ID in (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO like 'FILE-MES-ORDER-%'
 );

delete from RRL_PRODUCTION_ORDER
 where ORDER_NO like 'FILE-MES-ORDER-%';

delete from RRL_PROD_BATCH
 where PROD_BATCH_NO like 'FILE-MES-LOT-%';

delete from RRL_BOM_AUDIT
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'FILE-MES-BOM-%');

delete from RRL_BOM_LINE
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'FILE-MES-BOM-%');

delete from RRL_BOM
 where BOM_CODE like 'FILE-MES-BOM-%';

commit;

prompt [smoke] cleanup MES file exchange workflow done
