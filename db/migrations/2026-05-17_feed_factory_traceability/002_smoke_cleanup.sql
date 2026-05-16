prompt [migration 2026-05-17-002] Feed factory traceability API - smoke with cleanup

declare
  v_message_id varchar2(100) := 'SMOKE-20260517-002';
  v_batch_id number;
  v_raw_batch_id number;
  v_raw_usage_id number;
  v_crpt_code_id number;
  v_aggregation_id number;
  v_outbox_id number;
  v_file_log_id number;
  v_count number;
begin
  v_file_log_id := RRL_PRODUCTION_API.register_file_message(
    p_exchange_type => 'PRODUCTION_RELEASE',
    p_source_system => 'SMOKE',
    p_message_id => v_message_id,
    p_external_operation_id => 'SMOKE-OP-002',
    p_file_name => 'smoke_002.json',
    p_file_path => 'smoke/in/smoke_002.json',
    p_file_hash => 'smoke'
  );

  v_batch_id := RRL_PRODUCTION_API.create_prod_batch(
    p_prod_batch_no => 'SMOKE-BATCH-002',
    p_articul => 'SMOKE-ART',
    p_gtin => '00000000000000',
    p_product_name => 'Smoke product',
    p_total_quantity => 10,
    p_total_pack_count => 10,
    p_unit_code => 'PCS',
    p_ware_id => -999,
    p_source_system => 'SMOKE',
    p_source_message_id => v_message_id,
    p_external_operation_id => 'SMOKE-OP-002',
    p_external_batch_id => 'SMOKE-EXT-BATCH-002',
    p_mercury_required => 1,
    p_crpt_required => 1,
    p_created_by => 'SMOKE'
  );

  RRL_PRODUCTION_API.attach_pallet(
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-002',
    p_pallet_no => 1,
    p_quantity => 10,
    p_pack_count => 10,
    p_sscc => '000000000000000002',
    p_quality_status => 'READY',
    p_created_by => 'SMOKE'
  );

  v_raw_batch_id := RRL_PRODUCTION_API.register_raw_batch(
    p_raw_batch_no => 'SMOKE-RAW-002',
    p_articul => 'SMOKE-RAW-ART',
    p_supplier_id => 'SMOKE-SUPPLIER',
    p_quantity_initial => 100,
    p_quantity_available => 90,
    p_unit_code => 'KG',
    p_ware_id => -999,
    p_created_by => 'SMOKE'
  );

  v_raw_usage_id := RRL_PRODUCTION_API.add_raw_usage(
    p_prod_batch_id => v_batch_id,
    p_raw_batch_id => v_raw_batch_id,
    p_raw_articul => 'SMOKE-RAW-ART',
    p_quantity_fact => 10,
    p_unit_code => 'KG',
    p_used_by => 'SMOKE'
  );

  RRL_PRODUCTION_API.set_mercury_batch(
    p_prod_batch_id => v_batch_id,
    p_mercury_operation_id => 'SMOKE-MERCURY-OP-002',
    p_stock_entry_uuid => 'SMOKE-STOCK-ENTRY-UUID-002',
    p_vet_document_uuid => 'SMOKE-VSD-UUID-002',
    p_vet_document_status => 'READY'
  );

  v_crpt_code_id := RRL_PRODUCTION_API.add_crpt_code(
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-002',
    p_gtin => '00000000000000',
    p_cis => '010000000000000021SMOKE002',
    p_serial_no => 'SMOKE002',
    p_datamatrix_full => '010000000000000021SMOKE002',
    p_parent_sscc => '000000000000000002'
  );

  v_aggregation_id := RRL_PRODUCTION_API.create_aggregation(
    p_sscc => '000000000000000002',
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-002',
    p_aggregation_level => 'PALLET'
  );

  RRL_PRODUCTION_API.add_aggregation_item(
    p_aggregation_id => v_aggregation_id,
    p_child_type => 'CIS',
    p_child_cis => '010000000000000021SMOKE002',
    p_gtin => '00000000000000',
    p_prod_batch_id => v_batch_id
  );

  v_outbox_id := RRL_PRODUCTION_API.enqueue_event(
    p_system_code => 'CRPT',
    p_event_type => 'INTRODUCE',
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-002',
    p_document_no => 'SMOKE-DOC-002',
    p_payload_json => '{"smoke":true}',
    p_idempotency_key => 'SMOKE-OUTBOX-002'
  );

  RRL_PRODUCTION_API.mark_file_processed(
    p_message_id => v_message_id,
    p_prod_batch_id => v_batch_id,
    p_processed_by => 'SMOKE'
  );

  RRL_PRODUCTION_API.set_batch_status(
    p_prod_batch_id => v_batch_id,
    p_quality_status => 'READY',
    p_mercury_status => 'READY',
    p_crpt_status => 'READY',
    p_updated_by => 'SMOKE'
  );

  select count(*)
    into v_count
    from RRL_PROD_BATCH
   where PROD_BATCH_ID = v_batch_id;

  if v_count != 1 or v_file_log_id is null or v_raw_usage_id is null
     or v_crpt_code_id is null or v_aggregation_id is null or v_outbox_id is null then
    raise_application_error(-20002, 'RRL_PRODUCTION_API smoke failed.');
  end if;
end;
/

delete from RRL_CRPT_AGGREGATION_ITEMS
 where CHILD_CIS = '010000000000000021SMOKE002'
    or CHILD_SSCC = '000000000000000002'
    or PROD_BATCH_ID in (
      select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
    );

delete from RRL_CRPT_AGGREGATION
 where SSCC = '000000000000000002'
    or PROD_BATCH_ID in (
      select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
    );

delete from RRL_CRPT_CODES
 where CIS = '010000000000000021SMOKE002'
    or PROD_BATCH_ID in (
      select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
    );

delete from RRL_REGULATORY_OUTBOX
 where IDEMPOTENCY_KEY = 'SMOKE-OUTBOX-002'
    or PROD_BATCH_ID in (
      select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
    );

delete from RRL_MERCURY_BATCH
 where PROD_BATCH_ID in (
   select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
 );

delete from RRL_PROD_BATCH_PALLETS
 where UID_PALLET = 'SMOKE-PALLET-002'
    or PROD_BATCH_ID in (
      select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
    );

delete from RRL_PROD_RAW_USAGE
 where PROD_BATCH_ID in (
   select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-002'
 )
    or RAW_BATCH_ID in (
      select RAW_BATCH_ID from RRL_RAW_BATCH where RAW_BATCH_NO = 'SMOKE-RAW-002'
    );

delete from RRL_RAW_BATCH
 where RAW_BATCH_NO = 'SMOKE-RAW-002';

delete from RRL_FILE_EXCHANGE_LOG
 where MESSAGE_ID = 'SMOKE-20260517-002';

delete from RRL_PROD_BATCH
 where PROD_BATCH_NO = 'SMOKE-BATCH-002';

commit;

prompt [migration 2026-05-17-002] Smoke finished and cleanup committed.
