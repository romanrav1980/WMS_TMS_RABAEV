package RRL_REGULATORY_API as
  function upsert_mercury_site(
    p_site_code           varchar2,
    p_site_name           varchar2 default null,
    p_ware_id             number default null,
    p_enterprise_guid     varchar2 default null,
    p_enterprise_uuid     varchar2 default null,
    p_business_guid       varchar2 default null,
    p_business_uuid       varchar2 default null,
    p_address_text        varchar2 default null,
    p_active              number default 1,
    p_updated_by          varchar2 default user
  ) return number;

  function create_mercury_operation(
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_mercury_site_id     number default null,
    p_operation_type      varchar2,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_status              varchar2 default 'DRAFT',
    p_request_json        clob default null,
    p_created_by          varchar2 default user
  ) return number;

  procedure update_mercury_operation(
    p_operation_row_id    number,
    p_status              varchar2 default null,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_response_json       clob default null,
    p_last_error          varchar2 default null,
    p_updated_by          varchar2 default user
  );

  function write_journal(
    p_system_code         varchar2,
    p_entity_type         varchar2,
    p_entity_id           varchar2 default null,
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_uid_pallet          varchar2 default null,
    p_sscc                varchar2 default null,
    p_operation_type      varchar2,
    p_old_status          varchar2 default null,
    p_new_status          varchar2 default null,
    p_document_id         varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_payload_json        clob default null,
    p_message             varchar2 default null,
    p_created_by          varchar2 default user
  ) return number;

  function set_crpt_code_status(
    p_cis                 varchar2,
    p_code_status         varchar2,
    p_event_type          varchar2 default null,
    p_document_id         varchar2 default null,
    p_document_no         varchar2 default null,
    p_payload_json        clob default null,
    p_error_text          varchar2 default null,
    p_updated_by          varchar2 default user
  ) return number;
end RRL_REGULATORY_API;
