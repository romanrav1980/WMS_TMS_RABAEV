prompt [migration 2026-05-17-002] Feed factory traceability API - apply

create or replace package RRL_PRODUCTION_API as
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
/

create or replace package body RRL_PRODUCTION_API as
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
  ) return number is
    v_id number;
  begin
    if p_source_system is not null and p_source_message_id is not null then
      begin
        select PROD_BATCH_ID
          into v_id
          from RRL_PROD_BATCH
         where SOURCE_SYSTEM = p_source_system
           and SOURCE_MESSAGE_ID = p_source_message_id
           and nvl(EXTERNAL_BATCH_ID, '#') = nvl(p_external_batch_id, '#')
           and rownum = 1;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    begin
      select PROD_BATCH_ID
        into v_id
        from RRL_PROD_BATCH
       where PROD_BATCH_NO = p_prod_batch_no
         and nvl(ARTICUL, '#') = nvl(p_articul, '#')
         and nvl(WARE_ID, -1) = nvl(p_ware_id, -1)
         and rownum = 1;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_PROD_BATCH_SQ.nextval into v_id from dual;

    insert into RRL_PROD_BATCH (
      PROD_BATCH_ID,
      PROD_BATCH_NO,
      PRODUCTION_ORDER_ID,
      SOURCE_SYSTEM,
      SOURCE_MESSAGE_ID,
      EXTERNAL_OPERATION_ID,
      EXTERNAL_BATCH_ID,
      ARTICUL,
      MOD_ID,
      GTIN,
      PRODUCT_NAME,
      PRODUCED_DATE_FROM,
      PRODUCED_DATE_TO,
      EXPIRY_DATE_FROM,
      EXPIRY_DATE_TO,
      TOTAL_QUANTITY,
      TOTAL_PACK_COUNT,
      UNIT_CODE,
      WARE_ID,
      PRODUCTION_LINE,
      SHIFT_ID,
      QUALITY_STATUS,
      MERCURY_REQUIRED,
      CRPT_REQUIRED,
      MERCURY_STATUS,
      CRPT_STATUS,
      CREATED_AT,
      CREATED_BY
    ) values (
      v_id,
      p_prod_batch_no,
      p_production_order_id,
      p_source_system,
      p_source_message_id,
      p_external_operation_id,
      p_external_batch_id,
      p_articul,
      p_mod_id,
      p_gtin,
      p_product_name,
      p_produced_date_from,
      p_produced_date_to,
      p_expiry_date_from,
      p_expiry_date_to,
      p_total_quantity,
      p_total_pack_count,
      p_unit_code,
      p_ware_id,
      p_production_line,
      p_shift_id,
      'DRAFT',
      nvl(p_mercury_required, 0),
      nvl(p_crpt_required, 0),
      case when nvl(p_mercury_required, 0) = 1 then 'PENDING' else 'NOT_REQUIRED' end,
      case when nvl(p_crpt_required, 0) = 1 then 'PENDING' else 'NOT_REQUIRED' end,
      sysdate,
      p_created_by
    );

    return v_id;
  end create_prod_batch;

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
  ) is
  begin
    merge into RRL_PROD_BATCH_PALLETS d
    using (
      select p_prod_batch_id PROD_BATCH_ID,
             p_uid_pallet UID_PALLET
        from dual
    ) s
    on (d.PROD_BATCH_ID = s.PROD_BATCH_ID and d.UID_PALLET = s.UID_PALLET)
    when matched then update set
      d.PALLET_NO = nvl(p_pallet_no, d.PALLET_NO),
      d.QUANTITY = nvl(p_quantity, d.QUANTITY),
      d.PACK_COUNT = nvl(p_pack_count, d.PACK_COUNT),
      d.NET_WEIGHT = nvl(p_net_weight, d.NET_WEIGHT),
      d.GROSS_WEIGHT = nvl(p_gross_weight, d.GROSS_WEIGHT),
      d.SSCC = nvl(p_sscc, d.SSCC)
    when not matched then insert (
      PROD_BATCH_ID, UID_PALLET, PALLET_NO, QUANTITY, PACK_COUNT,
      NET_WEIGHT, GROSS_WEIGHT, SSCC, AGGREGATION_STATUS, CREATED_AT, CREATED_BY
    ) values (
      p_prod_batch_id, p_uid_pallet, p_pallet_no, p_quantity, p_pack_count,
      p_net_weight, p_gross_weight, p_sscc, 'DRAFT', sysdate, p_created_by
    );

    update RRL_PALLETS
       set PROD_BATCH_ID = p_prod_batch_id,
           SSCC = nvl(p_sscc, SSCC),
           QUALITY_STATUS = nvl(p_quality_status, QUALITY_STATUS)
     where UID_PALLET = p_uid_pallet;
  end attach_pallet;

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
  ) return number is
    v_id number;
  begin
    begin
      select RAW_BATCH_ID
        into v_id
        from RRL_RAW_BATCH
       where RAW_BATCH_NO = p_raw_batch_no
         and nvl(ARTICUL, '#') = nvl(p_articul, '#')
         and nvl(WARE_ID, -1) = nvl(p_ware_id, -1)
         and rownum = 1;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_RAW_BATCH_SQ.nextval into v_id from dual;

    insert into RRL_RAW_BATCH (
      RAW_BATCH_ID, RAW_BATCH_NO, ARTICUL, SUPPLIER_ID, PRODUCER_NAME,
      QUANTITY_INITIAL, QUANTITY_AVAILABLE, UNIT_CODE, WARE_ID,
      MERCURY_STOCK_ENTRY_UUID, MERCURY_VSD_UUID, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_raw_batch_no, p_articul, p_supplier_id, p_producer_name,
      p_quantity_initial, nvl(p_quantity_available, p_quantity_initial), p_unit_code, p_ware_id,
      p_mercury_stock_entry_uuid, p_mercury_vsd_uuid, sysdate, p_created_by
    );

    return v_id;
  end register_raw_batch;

  function add_raw_usage(
    p_prod_batch_id        number,
    p_raw_batch_id         number default null,
    p_raw_articul          varchar2 default null,
    p_quantity_planned     number default null,
    p_quantity_fact        number default null,
    p_unit_code            varchar2 default 'PCS',
    p_used_by              varchar2 default user
  ) return number is
    v_id number;
  begin
    select RRL_PROD_RAW_USAGE_SQ.nextval into v_id from dual;

    insert into RRL_PROD_RAW_USAGE (
      RAW_USAGE_ID, PROD_BATCH_ID, RAW_BATCH_ID, RAW_ARTICUL,
      QUANTITY_PLANNED, QUANTITY_FACT, UNIT_CODE, USED_AT, USED_BY
    ) values (
      v_id, p_prod_batch_id, p_raw_batch_id, p_raw_articul,
      p_quantity_planned, p_quantity_fact, p_unit_code, sysdate, p_used_by
    );

    return v_id;
  end add_raw_usage;

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
  ) is
  begin
    merge into RRL_MERCURY_BATCH d
    using (select p_prod_batch_id PROD_BATCH_ID from dual) s
    on (d.PROD_BATCH_ID = s.PROD_BATCH_ID)
    when matched then update set
      d.MERCURY_OPERATION_ID = nvl(p_mercury_operation_id, d.MERCURY_OPERATION_ID),
      d.STOCK_ENTRY_UUID = nvl(p_stock_entry_uuid, d.STOCK_ENTRY_UUID),
      d.STOCK_ENTRY_GUID = nvl(p_stock_entry_guid, d.STOCK_ENTRY_GUID),
      d.VET_DOCUMENT_UUID = nvl(p_vet_document_uuid, d.VET_DOCUMENT_UUID),
      d.VET_DOCUMENT_STATUS = nvl(p_vet_document_status, d.VET_DOCUMENT_STATUS),
      d.VET_DOCUMENT_TYPE = nvl(p_vet_document_type, d.VET_DOCUMENT_TYPE),
      d.VET_DOCUMENT_FORM = nvl(p_vet_document_form, d.VET_DOCUMENT_FORM),
      d.PRODUCT_ITEM_GUID = nvl(p_product_item_guid, d.PRODUCT_ITEM_GUID),
      d.PRODUCT_ITEM_NAME = nvl(p_product_item_name, d.PRODUCT_ITEM_NAME),
      d.LAST_ERROR = substr(p_last_error, 1, 4000),
      d.UPDATED_AT = sysdate
    when not matched then insert (
      PROD_BATCH_ID, MERCURY_OPERATION_ID, STOCK_ENTRY_UUID, STOCK_ENTRY_GUID,
      VET_DOCUMENT_UUID, VET_DOCUMENT_STATUS, VET_DOCUMENT_TYPE, VET_DOCUMENT_FORM,
      PRODUCT_ITEM_GUID, PRODUCT_ITEM_NAME, LAST_ERROR, UPDATED_AT
    ) values (
      p_prod_batch_id, p_mercury_operation_id, p_stock_entry_uuid, p_stock_entry_guid,
      p_vet_document_uuid, p_vet_document_status, p_vet_document_type, p_vet_document_form,
      p_product_item_guid, p_product_item_name, substr(p_last_error, 1, 4000), sysdate
    );

    update RRL_PROD_BATCH
       set MERCURY_STATUS = nvl(p_vet_document_status, MERCURY_STATUS),
           UPDATED_AT = sysdate,
           UPDATED_BY = user
     where PROD_BATCH_ID = p_prod_batch_id;
  end set_mercury_batch;

  function add_crpt_code(
    p_prod_batch_id        number,
    p_uid_pallet           varchar2 default null,
    p_gtin                 varchar2,
    p_cis                  varchar2,
    p_serial_no            varchar2 default null,
    p_datamatrix_full      varchar2 default null,
    p_parent_sscc          varchar2 default null
  ) return number is
    v_id number;
  begin
    begin
      select CRPT_CODE_ID
        into v_id
        from RRL_CRPT_CODES
       where CIS = p_cis;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_CRPT_CODES_SQ.nextval into v_id from dual;

    insert into RRL_CRPT_CODES (
      CRPT_CODE_ID, PROD_BATCH_ID, UID_PALLET, GTIN, CIS, SERIAL_NO,
      DATAMATRIX_FULL, CODE_STATUS, PARENT_SSCC, CREATED_AT
    ) values (
      v_id, p_prod_batch_id, p_uid_pallet, p_gtin, p_cis, p_serial_no,
      p_datamatrix_full, 'RESERVED', p_parent_sscc, sysdate
    );

    return v_id;
  end add_crpt_code;

  function create_aggregation(
    p_sscc                 varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_parent_sscc          varchar2 default null,
    p_aggregation_level    varchar2 default 'PALLET'
  ) return number is
    v_id number;
  begin
    begin
      select AGGREGATION_ID
        into v_id
        from RRL_CRPT_AGGREGATION
       where SSCC = p_sscc;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_CRPT_AGGREGATION_SQ.nextval into v_id from dual;

    insert into RRL_CRPT_AGGREGATION (
      AGGREGATION_ID, SSCC, PROD_BATCH_ID, UID_PALLET, PARENT_SSCC,
      AGGREGATION_LEVEL, AGGREGATION_STATUS, CREATED_AT
    ) values (
      v_id, p_sscc, p_prod_batch_id, p_uid_pallet, p_parent_sscc,
      p_aggregation_level, 'DRAFT', sysdate
    );

    if p_uid_pallet is not null then
      update RRL_PROD_BATCH_PALLETS
         set SSCC = p_sscc,
             AGGREGATION_STATUS = 'DRAFT'
       where PROD_BATCH_ID = p_prod_batch_id
         and UID_PALLET = p_uid_pallet;

      update RRL_PALLETS
         set SSCC = p_sscc
       where UID_PALLET = p_uid_pallet;
    end if;

    return v_id;
  end create_aggregation;

  procedure add_aggregation_item(
    p_aggregation_id       number,
    p_child_type           varchar2,
    p_child_cis            varchar2 default null,
    p_child_sscc           varchar2 default null,
    p_gtin                 varchar2 default null,
    p_prod_batch_id        number default null
  ) is
    v_count number;
    v_parent_sscc varchar2(32);
  begin
    select SSCC
      into v_parent_sscc
      from RRL_CRPT_AGGREGATION
     where AGGREGATION_ID = p_aggregation_id;

    select count(*)
      into v_count
      from RRL_CRPT_AGGREGATION_ITEMS
     where AGGREGATION_ID = p_aggregation_id
       and CHILD_TYPE = p_child_type
       and nvl(CHILD_CIS, '#') = nvl(p_child_cis, '#')
       and nvl(CHILD_SSCC, '#') = nvl(p_child_sscc, '#');

    if v_count = 0 then
      insert into RRL_CRPT_AGGREGATION_ITEMS (
        AGGREGATION_ID, CHILD_TYPE, CHILD_CIS, CHILD_SSCC,
        GTIN, PROD_BATCH_ID, CREATED_AT
      ) values (
        p_aggregation_id, p_child_type, p_child_cis, p_child_sscc,
        p_gtin, p_prod_batch_id, sysdate
      );
    end if;

    if p_child_type = 'CIS' and p_child_cis is not null then
      update RRL_CRPT_CODES
         set PARENT_SSCC = v_parent_sscc
       where CIS = p_child_cis;
    elsif p_child_type = 'SSCC' and p_child_sscc is not null then
      update RRL_CRPT_AGGREGATION
         set PARENT_SSCC = v_parent_sscc
       where SSCC = p_child_sscc;
    end if;
  end add_aggregation_item;

  function enqueue_event(
    p_system_code          varchar2,
    p_event_type           varchar2,
    p_prod_batch_id        number default null,
    p_uid_pallet           varchar2 default null,
    p_document_no          varchar2 default null,
    p_payload_json         clob default null,
    p_idempotency_key      varchar2 default null
  ) return number is
    v_id number;
  begin
    if p_idempotency_key is not null then
      begin
        select OUTBOX_ID
          into v_id
          from RRL_REGULATORY_OUTBOX
         where IDEMPOTENCY_KEY = p_idempotency_key
           and rownum = 1;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    select RRL_REGULATORY_OUTBOX_SQ.nextval into v_id from dual;

    insert into RRL_REGULATORY_OUTBOX (
      OUTBOX_ID, SYSTEM_CODE, EVENT_TYPE, PROD_BATCH_ID, UID_PALLET,
      DOCUMENT_NO, PAYLOAD_JSON, STATUS, TRY_COUNT, CREATED_AT, IDEMPOTENCY_KEY
    ) values (
      v_id, p_system_code, p_event_type, p_prod_batch_id, p_uid_pallet,
      p_document_no, p_payload_json, 'PENDING', 0, sysdate, p_idempotency_key
    );

    return v_id;
  end enqueue_event;

  procedure set_batch_status(
    p_prod_batch_id        number,
    p_quality_status       varchar2 default null,
    p_mercury_status       varchar2 default null,
    p_crpt_status          varchar2 default null,
    p_updated_by           varchar2 default user
  ) is
  begin
    update RRL_PROD_BATCH
       set QUALITY_STATUS = nvl(p_quality_status, QUALITY_STATUS),
           MERCURY_STATUS = nvl(p_mercury_status, MERCURY_STATUS),
           CRPT_STATUS = nvl(p_crpt_status, CRPT_STATUS),
           UPDATED_AT = sysdate,
           UPDATED_BY = p_updated_by
     where PROD_BATCH_ID = p_prod_batch_id;
  end set_batch_status;

  function register_file_message(
    p_exchange_type        varchar2,
    p_source_system        varchar2,
    p_message_id           varchar2,
    p_external_operation_id varchar2 default null,
    p_file_name            varchar2 default null,
    p_file_path            varchar2 default null,
    p_file_hash            varchar2 default null
  ) return number is
    v_id number;
  begin
    begin
      select FILE_LOG_ID
        into v_id
        from RRL_FILE_EXCHANGE_LOG
       where MESSAGE_ID = p_message_id;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_FILE_EXCHANGE_LOG_SQ.nextval into v_id from dual;

    insert into RRL_FILE_EXCHANGE_LOG (
      FILE_LOG_ID, EXCHANGE_TYPE, SOURCE_SYSTEM, MESSAGE_ID,
      EXTERNAL_OPERATION_ID, FILE_NAME, FILE_PATH, FILE_HASH,
      STATUS, RECEIVED_AT
    ) values (
      v_id, p_exchange_type, p_source_system, p_message_id,
      p_external_operation_id, p_file_name, p_file_path, p_file_hash,
      'RECEIVED', sysdate
    );

    return v_id;
  end register_file_message;

  procedure mark_file_processed(
    p_message_id           varchar2,
    p_prod_batch_id        number default null,
    p_processed_by         varchar2 default user
  ) is
  begin
    update RRL_FILE_EXCHANGE_LOG
       set STATUS = 'PROCESSED',
           ERROR_CODE = null,
           ERROR_TEXT = null,
           PROCESSED_AT = sysdate,
           PROCESSED_BY = p_processed_by,
           CREATED_PROD_BATCH_ID = nvl(p_prod_batch_id, CREATED_PROD_BATCH_ID)
     where MESSAGE_ID = p_message_id;
  end mark_file_processed;

  procedure mark_file_error(
    p_message_id           varchar2,
    p_error_code           varchar2,
    p_error_text           varchar2,
    p_processed_by         varchar2 default user
  ) is
  begin
    update RRL_FILE_EXCHANGE_LOG
       set STATUS = 'ERROR',
           ERROR_CODE = p_error_code,
           ERROR_TEXT = substr(p_error_text, 1, 4000),
           PROCESSED_AT = sysdate,
           PROCESSED_BY = p_processed_by
     where MESSAGE_ID = p_message_id;
  end mark_file_error;

  function get_setting(p_setting_key varchar2) return varchar2 is
    v_value varchar2(4000);
  begin
    select SETTING_VALUE
      into v_value
      from RRL_SYSTEM_SETTINGS
     where SETTING_KEY = p_setting_key;
    return v_value;
  exception
    when no_data_found then
      return null;
  end get_setting;

  procedure set_setting(
    p_setting_key          varchar2,
    p_setting_value        varchar2,
    p_description          varchar2 default null
  ) is
  begin
    merge into RRL_SYSTEM_SETTINGS d
    using (
      select p_setting_key SETTING_KEY,
             p_setting_value SETTING_VALUE,
             p_description DESCRIPTION
        from dual
    ) s
    on (d.SETTING_KEY = s.SETTING_KEY)
    when matched then update set
      d.SETTING_VALUE = s.SETTING_VALUE,
      d.DESCRIPTION = nvl(s.DESCRIPTION, d.DESCRIPTION),
      d.UPDATED_AT = sysdate,
      d.UPDATED_BY = user
    when not matched then insert (
      SETTING_KEY, SETTING_VALUE, DESCRIPTION, UPDATED_AT, UPDATED_BY
    ) values (
      s.SETTING_KEY, s.SETTING_VALUE, s.DESCRIPTION, sysdate, user
    );
  end set_setting;
end RRL_PRODUCTION_API;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-002-feed-factory-traceability-api' migration_id,
         'Feed factory traceability PL/SQL API package' description,
         '002_apply.sql' script_name,
         '002_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-002] Apply finished. Run 002_verify.sql.
