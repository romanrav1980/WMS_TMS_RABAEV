package body RRL_REGULATORY_API as
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
  ) return number is
    v_id number;
  begin
    begin
      select MERCURY_SITE_ID into v_id
        from RRL_MERCURY_SITE
       where SITE_CODE = p_site_code;
    exception
      when no_data_found then
        select RRL_MERCURY_SITE_SQ.nextval into v_id from dual;
        insert into RRL_MERCURY_SITE (
          MERCURY_SITE_ID, SITE_CODE, SITE_NAME, WARE_ID,
          ENTERPRISE_GUID, ENTERPRISE_UUID, BUSINESS_GUID, BUSINESS_UUID,
          ADDRESS_TEXT, ACTIVE, CREATED_AT, CREATED_BY
        ) values (
          v_id, p_site_code, p_site_name, p_ware_id,
          p_enterprise_guid, p_enterprise_uuid, p_business_guid, p_business_uuid,
          p_address_text, nvl(p_active, 1), sysdate, p_updated_by
        );
        return v_id;
    end;

    update RRL_MERCURY_SITE
       set SITE_NAME = nvl(p_site_name, SITE_NAME),
           WARE_ID = nvl(p_ware_id, WARE_ID),
           ENTERPRISE_GUID = nvl(p_enterprise_guid, ENTERPRISE_GUID),
           ENTERPRISE_UUID = nvl(p_enterprise_uuid, ENTERPRISE_UUID),
           BUSINESS_GUID = nvl(p_business_guid, BUSINESS_GUID),
           BUSINESS_UUID = nvl(p_business_uuid, BUSINESS_UUID),
           ADDRESS_TEXT = nvl(p_address_text, ADDRESS_TEXT),
           ACTIVE = nvl(p_active, ACTIVE),
           UPDATED_AT = sysdate,
           UPDATED_BY = p_updated_by
     where MERCURY_SITE_ID = v_id;

    return v_id;
  end upsert_mercury_site;

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
  ) return number is
    v_id number;
    v_journal_id number;
  begin
    if p_mercury_operation_id is not null then
      begin
        select MERCURY_OPERATION_ROW_ID into v_id
          from RRL_MERCURY_OPERATION
         where MERCURY_OPERATION_ID = p_mercury_operation_id
           and rownum = 1;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    select RRL_MERCURY_OPERATION_SQ.nextval into v_id from dual;

    insert into RRL_MERCURY_OPERATION (
      MERCURY_OPERATION_ROW_ID, PROD_BATCH_ID, RAW_BATCH_ID, MERCURY_SITE_ID,
      OPERATION_TYPE, MERCURY_OPERATION_ID, EXTERNAL_OPERATION_ID, STATUS,
      REQUEST_JSON, STARTED_AT, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_prod_batch_id, p_raw_batch_id, p_mercury_site_id,
      p_operation_type, p_mercury_operation_id, p_external_operation_id, nvl(p_status, 'DRAFT'),
      p_request_json, case when nvl(p_status, 'DRAFT') in ('SENT', 'PROCESSING') then sysdate else null end,
      sysdate, p_created_by
    );

    v_journal_id := write_journal(
      p_system_code => 'MERCURY',
      p_entity_type => 'MERCURY_OPERATION',
      p_entity_id => to_char(v_id),
      p_prod_batch_id => p_prod_batch_id,
      p_raw_batch_id => p_raw_batch_id,
      p_operation_type => p_operation_type,
      p_new_status => nvl(p_status, 'DRAFT'),
      p_external_operation_id => p_external_operation_id,
      p_payload_json => p_request_json,
      p_created_by => p_created_by
    );

    if p_prod_batch_id is not null and p_mercury_site_id is not null then
      update RRL_PROD_BATCH
         set MERCURY_SITE_ID = p_mercury_site_id,
             UPDATED_AT = sysdate,
             UPDATED_BY = p_created_by
       where PROD_BATCH_ID = p_prod_batch_id;
    end if;

    return v_id;
  end create_mercury_operation;

  procedure update_mercury_operation(
    p_operation_row_id    number,
    p_status              varchar2 default null,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_response_json       clob default null,
    p_last_error          varchar2 default null,
    p_updated_by          varchar2 default user
  ) is
    v_old_status varchar2(50);
    v_new_status varchar2(50);
    v_prod_batch_id number;
    v_raw_batch_id number;
    v_journal_id number;
  begin
    select STATUS, PROD_BATCH_ID, RAW_BATCH_ID
      into v_old_status, v_prod_batch_id, v_raw_batch_id
      from RRL_MERCURY_OPERATION
     where MERCURY_OPERATION_ROW_ID = p_operation_row_id;

    v_new_status := nvl(p_status, v_old_status);

    update RRL_MERCURY_OPERATION
       set STATUS = v_new_status,
           MERCURY_OPERATION_ID = nvl(p_mercury_operation_id, MERCURY_OPERATION_ID),
           EXTERNAL_OPERATION_ID = nvl(p_external_operation_id, EXTERNAL_OPERATION_ID),
           RESPONSE_JSON = nvl(p_response_json, RESPONSE_JSON),
           LAST_ERROR = substr(p_last_error, 1, 4000),
           FINISHED_AT = case when v_new_status in ('ACCEPTED', 'REJECTED', 'ERROR', 'DONE') then sysdate else FINISHED_AT end,
           UPDATED_AT = sysdate,
           UPDATED_BY = p_updated_by
     where MERCURY_OPERATION_ROW_ID = p_operation_row_id;

    v_journal_id := write_journal(
      p_system_code => 'MERCURY',
      p_entity_type => 'MERCURY_OPERATION',
      p_entity_id => to_char(p_operation_row_id),
      p_prod_batch_id => v_prod_batch_id,
      p_raw_batch_id => v_raw_batch_id,
      p_operation_type => 'STATUS',
      p_old_status => v_old_status,
      p_new_status => v_new_status,
      p_external_operation_id => p_external_operation_id,
      p_payload_json => p_response_json,
      p_message => p_last_error,
      p_created_by => p_updated_by
    );
  end update_mercury_operation;

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
  ) return number is
    v_id number;
  begin
    select RRL_REG_OPERATION_JOURNAL_SQ.nextval into v_id from dual;

    insert into RRL_REG_OPERATION_JOURNAL (
      JOURNAL_ID, SYSTEM_CODE, ENTITY_TYPE, ENTITY_ID, PROD_BATCH_ID, RAW_BATCH_ID,
      UID_PALLET, SSCC, OPERATION_TYPE, OLD_STATUS, NEW_STATUS, DOCUMENT_ID,
      EXTERNAL_OPERATION_ID, PAYLOAD_JSON, MESSAGE, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_system_code, p_entity_type, p_entity_id, p_prod_batch_id, p_raw_batch_id,
      p_uid_pallet, p_sscc, p_operation_type, p_old_status, p_new_status, p_document_id,
      p_external_operation_id, p_payload_json, substr(p_message, 1, 4000), sysdate, p_created_by
    );

    return v_id;
  end write_journal;

  function set_crpt_code_status(
    p_cis                 varchar2,
    p_code_status         varchar2,
    p_event_type          varchar2 default null,
    p_document_id         varchar2 default null,
    p_document_no         varchar2 default null,
    p_payload_json        clob default null,
    p_error_text          varchar2 default null,
    p_updated_by          varchar2 default user
  ) return number is
    v_code_id number;
    v_prod_batch_id number;
    v_uid_pallet varchar2(50);
    v_parent_sscc varchar2(32);
    v_old_status varchar2(50);
    v_circ_id number;
    v_event_type varchar2(30);
    v_journal_id number;
  begin
    select CRPT_CODE_ID, PROD_BATCH_ID, UID_PALLET, PARENT_SSCC, CODE_STATUS
      into v_code_id, v_prod_batch_id, v_uid_pallet, v_parent_sscc, v_old_status
      from RRL_CRPT_CODES
     where CIS = p_cis;

    v_event_type := upper(p_event_type);

    update RRL_CRPT_CODES
       set CODE_STATUS = p_code_status,
           INTRODUCED_AT = case when v_event_type = 'INTRODUCE' then sysdate else INTRODUCED_AT end,
           WITHDRAWN_AT = case when v_event_type = 'WITHDRAW' then sysdate else WITHDRAWN_AT end,
           INTRODUCTION_DOCUMENT_ID = case when v_event_type = 'INTRODUCE' then p_document_id else INTRODUCTION_DOCUMENT_ID end,
           WITHDRAWAL_DOCUMENT_ID = case when v_event_type = 'WITHDRAW' then p_document_id else WITHDRAWAL_DOCUMENT_ID end,
           LAST_STATUS_AT = sysdate,
           LAST_ERROR = substr(p_error_text, 1, 4000)
     where CRPT_CODE_ID = v_code_id;

    if v_event_type in ('INTRODUCE', 'WITHDRAW') then
      select RRL_CRPT_CIRCULATION_SQ.nextval into v_circ_id from dual;

      insert into RRL_CRPT_CIRCULATION (
        CIRCULATION_ID, EVENT_TYPE, PROD_BATCH_ID, UID_PALLET, SSCC, CIS,
        DOCUMENT_ID, DOCUMENT_NO, STATUS, PAYLOAD_JSON, ACCEPTED_AT,
        ERROR_TEXT, CREATED_AT, CREATED_BY
      ) values (
        v_circ_id, v_event_type, v_prod_batch_id, v_uid_pallet, v_parent_sscc, p_cis,
        p_document_id, p_document_no, p_code_status, p_payload_json,
        case when p_error_text is null then sysdate else null end,
        substr(p_error_text, 1, 4000), sysdate, p_updated_by
      );
    end if;

    v_journal_id := write_journal(
      p_system_code => 'CRPT',
      p_entity_type => 'CRPT_CODE',
      p_entity_id => p_cis,
      p_prod_batch_id => v_prod_batch_id,
      p_uid_pallet => v_uid_pallet,
      p_sscc => v_parent_sscc,
      p_operation_type => nvl(v_event_type, 'STATUS'),
      p_old_status => v_old_status,
      p_new_status => p_code_status,
      p_document_id => p_document_id,
      p_payload_json => p_payload_json,
      p_message => p_error_text,
      p_created_by => p_updated_by
    );

    return v_code_id;
  end set_crpt_code_status;
end RRL_REGULATORY_API;
