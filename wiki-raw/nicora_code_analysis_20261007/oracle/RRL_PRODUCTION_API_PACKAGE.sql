package RRL_PRODUCTION_API as
  function create_prod_batch(
    p_prod_batch_no        varchar2,
    p_articul              varchar2 default null,
    p_mod_id               number default null,
    p_gtin                 varchar2 default null,
    p_product_name         varchar2 default null,
    p_total_quantity       number default null,
    p_total_pack_count     number default null,
    p_unit_code            varchar2 default 'PCS',
    p_ware_id              number default null,
    p_source_system        varchar2 default null,
    p_source_message_id    varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_external_batch_id    varchar2 default null,
    p_production_order_id  number default null,
    p_produced_date_from   date default null,
    p_produced_date_to     date default null,
    p_expiry_date_from     date default null,
    p_expiry_date_to       date default null,
    p_production_line      varchar2 default null,
    p_shift_id             varchar2 default null,
    p_mercury_required     number default 0,
    p_crpt_required        number default 0,
    p_created_by           varchar2 default user
  ) return number;

  procedure attach_pallet(
    p_prod_batch_id        number,
    p_uid_pallet           varchar2,
    p_pallet_no            number default null,
    p_quantity             number default null,
    p_pack_count           number default null,
    p_net_weight           number default null,
    p_gross_weight         number default null,
    p_sscc                 varchar2 default null,
    p_quality_status       varchar2 default null,
    p_created_by           varchar2 default user
  );

  function register_raw_batch(
    p_raw_batch_no         varchar2,
    p_articul              varchar2 default null,
    p_supplier_id          varchar2 default null,
    p_producer_name        varchar2 default null,
    p_quantity_initial     number default null,
    p_quantity_available   number default null,
    p_unit_code            varchar2 default 'PCS',
    p_ware_id              number default null,
    p_mercury_stock_entry_uuid varchar2 default null,
    p_mercury_vsd_uuid     varchar2 default null,
    p_created_by           varchar2 default user
  ) return number;

  function add_raw_usage(
    p_prod_batch_id        number,
    p_raw_batch_id         number default null,
    p_raw_articul          varchar2 default null,
    p_quantity_planned     number default null,
    p_quantity_fact        number default null,
    p_unit_code            varchar2 default 'PCS',
    p_used_by              varchar2 default user
  ) return number;

  procedure set_mercury_batch(
    p_prod_batch_id        number,
    p_mercury_operation_id varchar2 default null,
    p_stock_entry_uuid     varchar2 default null,
    p_stock_entry_guid     varchar2 default null,
    p_vet_document_uuid    varchar2 default null,
    p_vet_document_status  varchar2 default null,
    p_vet_document_type    varchar2 default null,
    p_vet_document_form    varchar2 default null,
    p_product_item_guid    varchar2 default null,
    p_product_item_name    varchar2 default null,
    p_last_error           varchar2 default null
  );

  function add_crpt_code(
    p_prod_batch_id        number,
    p_uid_pallet           varchar2 default null,
    p_gtin                 varchar2,
    p_cis                  varchar2,
    p_serial_no            varchar2 default null,
    p_datamatrix_full      varchar2 default null,
    p_parent_sscc          varchar2 default null
  ) return number;

  function create_aggregation(
    p_sscc                 varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_parent_sscc          varchar2 default null,
    p_aggregation_level    varchar2 default 'PALLET'
  ) return number;

  procedure add_aggregation_item(
    p_aggregation_id       number,
    p_child_type           varchar2,
    p_child_cis            varchar2 default null,
    p_child_sscc           varchar2 default null,
    p_gtin                 varchar2 default null,
    p_prod_batch_id        number default null
  );

  function enqueue_event(
    p_system_code          varchar2,
    p_event_type           varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_document_no          varchar2 default null,
    p_payload_json         clob default null,
    p_idempotency_key      varchar2 default null
  ) return number;

  procedure set_batch_status(
    p_prod_batch_id        number,
    p_quality_status       varchar2 default null,
    p_mercury_status       varchar2 default null,
    p_crpt_status          varchar2 default null,
    p_updated_by           varchar2 default user
  );

  function register_file_message(
    p_exchange_type        varchar2,
    p_source_system        varchar2,
    p_message_id           varchar2,
    p_external_operation_id varchar2 default null,
    p_file_name            varchar2 default null,
    p_file_path            varchar2 default null,
    p_file_hash            varchar2 default null
  ) return number;

  procedure mark_file_processed(
    p_message_id           varchar2,
    p_prod_batch_id        number default null,
    p_processed_by         varchar2 default user
  );

  procedure mark_file_error(
    p_message_id           varchar2,
    p_error_code           varchar2,
    p_error_text           varchar2,
    p_processed_by         varchar2 default user
  );

  function get_setting(p_setting_key varchar2) return varchar2;

  procedure set_setting(
    p_setting_key          varchar2,
    p_setting_value        varchar2,
    p_description          varchar2 default null
  );
end RRL_PRODUCTION_API;
