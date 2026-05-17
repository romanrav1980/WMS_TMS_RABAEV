-- 2026-05-17-008 smoke test.
-- Creates only fixed SMOKE-008 keys. Run 008_smoke_cleanup.sql after worker verification.

declare
  v_trace_event_id number;
  v_trace_edge_id number;
  v_outbox_id number;
  v_hold_id number;
begin
  v_trace_event_id := RRL_TRACEABILITY_API.add_trace_event(
    p_event_type => 'FinishedGoodsLotReleased',
    p_entity_type => 'PROD_BATCH',
    p_entity_id => 'SMOKE-008-BATCH',
    p_source_system => 'SMOKE',
    p_correlation_id => 'SMOKE-008',
    p_idempotency_key => 'SMOKE-008-TRACE-EVENT',
    p_payload_json => '{"smoke":true}',
    p_created_by => 'SMOKE'
  );

  v_trace_edge_id := RRL_TRACEABILITY_API.add_trace_edge(
    p_from_entity_type => 'RAW_BATCH',
    p_from_entity_id => 'SMOKE-008-RAW',
    p_to_entity_type => 'PROD_BATCH',
    p_to_entity_id => 'SMOKE-008-BATCH',
    p_edge_type => 'CONSUMED_IN',
    p_quantity => 1,
    p_unit_code => 'KG',
    p_trace_event_id => v_trace_event_id,
    p_created_by => 'SMOKE'
  );

  v_outbox_id := RRL_TRACEABILITY_API.enqueue_event(
    p_event_type => 'MercuryOperationRequested',
    p_aggregate_type => 'PROD_BATCH',
    p_aggregate_id => 'SMOKE-008-BATCH',
    p_idempotency_key => 'SMOKE-008-OUTBOX-MERCURY',
    p_payload_json => '{"smoke":true,"target":"MERCURY"}',
    p_target_system => 'MERCURY',
    p_correlation_id => 'SMOKE-008',
    p_max_try_count => 3
  );

  v_hold_id := RRL_TRACEABILITY_API.create_quality_hold(
    p_entity_type => 'PROD_BATCH',
    p_entity_id => 'SMOKE-008-BATCH',
    p_reason_code => 'SMOKE',
    p_reason_text => 'Smoke hold',
    p_created_by => 'SMOKE'
  );
end;
/

commit;

select 'SMOKE-008-TRACE-EVENT' check_name,
       count(*) rows_found
  from RRL_TRACE_EVENT
 where IDEMPOTENCY_KEY = 'SMOKE-008-TRACE-EVENT';

select 'SMOKE-008-OUTBOX' check_name,
       EVENT_OUTBOX_ID,
       STATUS
  from RRL_EVENT_OUTBOX
 where IDEMPOTENCY_KEY = 'SMOKE-008-OUTBOX-MERCURY';
