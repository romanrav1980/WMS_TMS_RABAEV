-- 2026-05-17-008 smoke cleanup.
-- Cleans only fixed SMOKE-008 keys created by local smoke tests.

delete from RRL_ADAPTER_REQUEST_LOG
 where BUSINESS_KEY like '%SMOKE-008%'
    or EVENT_OUTBOX_ID in (
      select EVENT_OUTBOX_ID
        from RRL_EVENT_OUTBOX
       where IDEMPOTENCY_KEY like 'SMOKE-008%'
          or AGGREGATE_ID like 'SMOKE-008%'
    );

delete from RRL_EVENT_OUTBOX
 where IDEMPOTENCY_KEY like 'SMOKE-008%';

delete from RRL_TRACE_EDGE
 where TRACE_EVENT_ID in (
   select TRACE_EVENT_ID
     from RRL_TRACE_EVENT
    where IDEMPOTENCY_KEY like 'SMOKE-008%'
 );

delete from RRL_TRACE_EVENT
 where IDEMPOTENCY_KEY like 'SMOKE-008%';

delete from RRL_QUALITY_HOLD
 where ENTITY_ID like 'SMOKE-008%';

commit;

select 'SMOKE-008-TRACE-EVENT' check_name,
       count(*) rows_left
  from RRL_TRACE_EVENT
 where IDEMPOTENCY_KEY like 'SMOKE-008%';

select 'SMOKE-008-OUTBOX' check_name,
       count(*) rows_left
  from RRL_EVENT_OUTBOX
 where IDEMPOTENCY_KEY like 'SMOKE-008%';

select 'SMOKE-008-ADAPTER' check_name,
       count(*) rows_left
  from RRL_ADAPTER_REQUEST_LOG
 where BUSINESS_KEY like 'SMOKE-008%';

select 'SMOKE-008-QA-HOLD' check_name,
       count(*) rows_left
  from RRL_QUALITY_HOLD
 where ENTITY_ID like 'SMOKE-008%';
