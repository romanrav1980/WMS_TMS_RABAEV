prompt [migration 2026-05-17-003] Smoke with cleanup

declare
  v_site_id number;
  v_batch_id number;
  v_code_id number;
  v_agg_id number;
  v_operation_id number;
  v_journal_id number;
begin
  v_site_id := RRL_REGULATORY_API.upsert_mercury_site(
    p_site_code => 'SMOKE-SITE-003',
    p_site_name => 'Smoke Mercury site',
    p_ware_id => -3,
    p_enterprise_guid => 'SMOKE-ENTERPRISE-GUID-003',
    p_enterprise_uuid => 'SMOKE-ENTERPRISE-UUID-003',
    p_business_guid => 'SMOKE-BUSINESS-GUID-003',
    p_business_uuid => 'SMOKE-BUSINESS-UUID-003',
    p_address_text => 'Smoke address',
    p_updated_by => 'SMOKE'
  );

  v_batch_id := RRL_PRODUCTION_API.create_prod_batch(
    p_prod_batch_no => 'SMOKE-BATCH-003',
    p_articul => 'SMOKE003',
    p_gtin => '04601234567893',
    p_product_name => 'Smoke feed product 003',
    p_total_quantity => 10,
    p_total_pack_count => 1,
    p_ware_id => -3,
    p_source_system => 'SMOKE',
    p_source_message_id => 'SMOKE-20260517-003',
    p_expiry_date_from => trunc(sysdate) + 180,
    p_expiry_date_to => trunc(sysdate) + 180,
    p_mercury_required => 1,
    p_crpt_required => 1,
    p_created_by => 'SMOKE'
  );

  update RRL_PROD_BATCH
     set MERCURY_SITE_ID = v_site_id
   where PROD_BATCH_ID = v_batch_id;

  v_code_id := RRL_PRODUCTION_API.add_crpt_code(
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-003',
    p_gtin => '04601234567893',
    p_cis => 'SMOKE-CIS-003',
    p_serial_no => 'SMOKE-SERIAL-003',
    p_datamatrix_full => '010460123456789321SMOKE-SERIAL-003',
    p_parent_sscc => '000000000000000003'
  );

  v_agg_id := RRL_PRODUCTION_API.create_aggregation(
    p_sscc => '000000000000000003',
    p_prod_batch_id => v_batch_id,
    p_uid_pallet => 'SMOKE-PALLET-003',
    p_aggregation_level => 'PALLET'
  );

  RRL_PRODUCTION_API.add_aggregation_item(
    p_aggregation_id => v_agg_id,
    p_child_type => 'CIS',
    p_child_cis => 'SMOKE-CIS-003',
    p_gtin => '04601234567893',
    p_prod_batch_id => v_batch_id
  );

  v_operation_id := RRL_REGULATORY_API.create_mercury_operation(
    p_prod_batch_id => v_batch_id,
    p_mercury_site_id => v_site_id,
    p_operation_type => 'PRODUCTION',
    p_mercury_operation_id => 'SMOKE-MERCURY-OP-003',
    p_status => 'SENT',
    p_request_json => '{"smoke":true}',
    p_created_by => 'SMOKE'
  );

  RRL_REGULATORY_API.update_mercury_operation(
    p_operation_row_id => v_operation_id,
    p_status => 'ACCEPTED',
    p_response_json => '{"accepted":true}',
    p_updated_by => 'SMOKE'
  );

  v_journal_id := RRL_REGULATORY_API.set_crpt_code_status(
    p_cis => 'SMOKE-CIS-003',
    p_code_status => 'INTRODUCED',
    p_event_type => 'INTRODUCE',
    p_document_id => 'SMOKE-CRPT-DOC-003',
    p_document_no => 'SMOKE-CRPT-DOC-NO-003',
    p_payload_json => '{"event":"INTRODUCE"}',
    p_updated_by => 'SMOKE'
  );

  if v_site_id is null or v_batch_id is null or v_code_id is null
     or v_agg_id is null or v_operation_id is null or v_journal_id is null then
    raise_application_error(-20003, 'RRL_REGULATORY_API smoke failed.');
  end if;
end;
/

delete from RRL_CRPT_CIRCULATION where CIS = 'SMOKE-CIS-003';
delete from RRL_REG_OPERATION_JOURNAL
 where CREATED_BY = 'SMOKE'
   and (ENTITY_ID in ('SMOKE-CIS-003', 'SMOKE-MERCURY-OP-003')
        or PROD_BATCH_ID in (select PROD_BATCH_ID from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-003'));
delete from RRL_MERCURY_OPERATION where MERCURY_OPERATION_ID = 'SMOKE-MERCURY-OP-003';
delete from RRL_CRPT_AGGREGATION_ITEMS where CHILD_CIS = 'SMOKE-CIS-003' or CHILD_SSCC = '000000000000000003';
delete from RRL_CRPT_AGGREGATION where SSCC = '000000000000000003';
delete from RRL_CRPT_CODES where CIS = 'SMOKE-CIS-003';
delete from RRL_PROD_BATCH_PALLETS where UID_PALLET = 'SMOKE-PALLET-003';
delete from RRL_PROD_BATCH where PROD_BATCH_NO = 'SMOKE-BATCH-003';
delete from RRL_MERCURY_SITE where SITE_CODE = 'SMOKE-SITE-003';
commit;

select 'SMOKE-BATCH-003' check_name, count(*) rows_left
  from RRL_PROD_BATCH
 where PROD_BATCH_NO = 'SMOKE-BATCH-003'
union all
select 'SMOKE-CIS-003', count(*)
  from RRL_CRPT_CODES
 where CIS = 'SMOKE-CIS-003'
union all
select 'SMOKE-SITE-003', count(*)
  from RRL_MERCURY_SITE
 where SITE_CODE = 'SMOKE-SITE-003';

prompt [migration 2026-05-17-003] Smoke with cleanup finished.
