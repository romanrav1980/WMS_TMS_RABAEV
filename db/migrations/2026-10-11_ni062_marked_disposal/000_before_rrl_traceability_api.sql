create or replace package RRL_TRACEABILITY_API as
  function add_trace_event(
    p_event_type       varchar2,
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_source_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_idempotency_key  varchar2 default null,
    p_payload_json     clob default null,
    p_created_by       varchar2 default null
  ) return number;

  function add_trace_edge(
    p_from_entity_type varchar2,
    p_from_entity_id   varchar2,
    p_to_entity_type   varchar2,
    p_to_entity_id     varchar2,
    p_edge_type        varchar2,
    p_quantity         number default null,
    p_unit_code        varchar2 default null,
    p_trace_event_id   number default null,
    p_created_by       varchar2 default null
  ) return number;

  function enqueue_event(
    p_event_type       varchar2,
    p_aggregate_type   varchar2,
    p_aggregate_id     varchar2,
    p_idempotency_key  varchar2,
    p_payload_json     clob,
    p_target_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_max_try_count    number default 10
  ) return number;

  function lock_next_outbox(
    p_worker_id        varchar2,
    p_target_system    varchar2 default null
  ) return number;

  procedure mark_outbox_done(
    p_event_outbox_id  number,
    p_status           varchar2 default 'DONE',
    p_error_text       varchar2 default null
  );

  procedure mark_outbox_error(
    p_event_outbox_id      number,
    p_error_text           varchar2,
    p_retry_delay_minutes  number default 5,
    p_dead_letter          number default 0
  );

  function add_adapter_request(
    p_system_code          varchar2,
    p_request_kind         varchar2,
    p_event_outbox_id      number default null,
    p_business_key         varchar2 default null,
    p_cert_alias           varchar2 default null,
    p_cert_thumbprint      varchar2 default null,
    p_signature_status     varchar2 default null,
    p_request_json         clob default null,
    p_status               varchar2 default 'STARTED',
    p_try_no               number default 1
  ) return number;

  procedure update_adapter_request(
    p_adapter_request_id   number,
    p_response_json        clob default null,
    p_external_request_id  varchar2 default null,
    p_external_document_id varchar2 default null,
    p_external_status      varchar2 default null,
    p_http_status          number default null,
    p_status               varchar2 default 'DONE',
    p_error_code           varchar2 default null,
    p_error_text           varchar2 default null
  );

  function create_quality_hold(
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_reason_code      varchar2 default null,
    p_reason_text      varchar2 default null,
    p_created_by       varchar2 default null
  ) return number;

  procedure release_quality_hold(
    p_quality_hold_id  number,
    p_released_by      varchar2 default null,
    p_release_reason   varchar2 default null
  );
end RRL_TRACEABILITY_API;
/

create or replace package body RRL_TRACEABILITY_API as
  function add_trace_event(
    p_event_type       varchar2,
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_source_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_idempotency_key  varchar2 default null,
    p_payload_json     clob default null,
    p_created_by       varchar2 default null
  ) return number is
    v_id number;
  begin
    if p_idempotency_key is not null then
      begin
        select TRACE_EVENT_ID into v_id
          from RRL_TRACE_EVENT
         where IDEMPOTENCY_KEY = p_idempotency_key;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    select RRL_TRACE_EVENT_SQ.nextval into v_id from dual;

    insert into RRL_TRACE_EVENT (
      TRACE_EVENT_ID, EVENT_TYPE, ENTITY_TYPE, ENTITY_ID, SOURCE_SYSTEM,
      CORRELATION_ID, IDEMPOTENCY_KEY, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(upper(p_event_type), 1, 80), substr(upper(p_entity_type), 1, 50),
      substr(p_entity_id, 1, 100), substr(upper(p_source_system), 1, 30),
      substr(p_correlation_id, 1, 100), substr(p_idempotency_key, 1, 100),
      p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );

    return v_id;
  end add_trace_event;

  function add_trace_edge(
    p_from_entity_type varchar2,
    p_from_entity_id   varchar2,
    p_to_entity_type   varchar2,
    p_to_entity_id     varchar2,
    p_edge_type        varchar2,
    p_quantity         number default null,
    p_unit_code        varchar2 default null,
    p_trace_event_id   number default null,
    p_created_by       varchar2 default null
  ) return number is
    v_id number;
  begin
    select RRL_TRACE_EDGE_SQ.nextval into v_id from dual;

    insert into RRL_TRACE_EDGE (
      TRACE_EDGE_ID, FROM_ENTITY_TYPE, FROM_ENTITY_ID, TO_ENTITY_TYPE, TO_ENTITY_ID,
      EDGE_TYPE, QUANTITY, UNIT_CODE, TRACE_EVENT_ID, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(upper(p_from_entity_type), 1, 50), substr(p_from_entity_id, 1, 100),
      substr(upper(p_to_entity_type), 1, 50), substr(p_to_entity_id, 1, 100),
      substr(upper(p_edge_type), 1, 50), p_quantity, substr(upper(p_unit_code), 1, 20),
      p_trace_event_id, sysdate, substr(p_created_by, 1, 50)
    );

    return v_id;
  end add_trace_edge;

  function enqueue_event(
    p_event_type       varchar2,
    p_aggregate_type   varchar2,
    p_aggregate_id     varchar2,
    p_idempotency_key  varchar2,
    p_payload_json     clob,
    p_target_system    varchar2 default null,
    p_correlation_id   varchar2 default null,
    p_max_try_count    number default 10
  ) return number is
    v_id number;
  begin
    begin
      select EVENT_OUTBOX_ID into v_id
        from RRL_EVENT_OUTBOX
       where IDEMPOTENCY_KEY = p_idempotency_key;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_EVENT_OUTBOX_SQ.nextval into v_id from dual;

    insert into RRL_EVENT_OUTBOX (
      EVENT_OUTBOX_ID, EVENT_TYPE, AGGREGATE_TYPE, AGGREGATE_ID, TARGET_SYSTEM,
      CORRELATION_ID, IDEMPOTENCY_KEY, PAYLOAD_JSON, STATUS, TRY_COUNT,
      MAX_TRY_COUNT, CREATED_AT
    ) values (
      v_id, substr(upper(p_event_type), 1, 80), substr(upper(p_aggregate_type), 1, 50),
      substr(p_aggregate_id, 1, 100), substr(upper(p_target_system), 1, 30),
      substr(p_correlation_id, 1, 100), substr(p_idempotency_key, 1, 100),
      p_payload_json, 'PENDING', 0, nvl(p_max_try_count, 10), sysdate
    );

    return v_id;
  end enqueue_event;

  function lock_next_outbox(
    p_worker_id        varchar2,
    p_target_system    varchar2 default null
  ) return number is
    v_id number;
  begin
    select EVENT_OUTBOX_ID
      into v_id
      from RRL_EVENT_OUTBOX
     where EVENT_OUTBOX_ID = (
       select EVENT_OUTBOX_ID
         from (
           select EVENT_OUTBOX_ID
             from RRL_EVENT_OUTBOX
            where STATUS in ('PENDING', 'RETRY')
              and (NEXT_RETRY_AT is null or NEXT_RETRY_AT <= sysdate)
              and (p_target_system is null or TARGET_SYSTEM = upper(p_target_system))
            order by CREATED_AT, EVENT_OUTBOX_ID
         )
        where rownum = 1
     )
       for update skip locked;

    update RRL_EVENT_OUTBOX
       set STATUS = 'LOCKED',
           LOCKED_BY = substr(p_worker_id, 1, 100),
           LOCKED_AT = sysdate
     where EVENT_OUTBOX_ID = v_id;

    return v_id;
  exception
    when no_data_found then
      return null;
  end lock_next_outbox;

  procedure mark_outbox_done(
    p_event_outbox_id  number,
    p_status           varchar2 default 'DONE',
    p_error_text       varchar2 default null
  ) is
  begin
    update RRL_EVENT_OUTBOX
       set STATUS = substr(upper(nvl(p_status, 'DONE')), 1, 30),
           LAST_ERROR = substr(p_error_text, 1, 4000),
           SENT_AT = nvl(SENT_AT, sysdate),
           FINISHED_AT = sysdate,
           LOCKED_BY = null,
           LOCKED_AT = null
     where EVENT_OUTBOX_ID = p_event_outbox_id;
  end mark_outbox_done;

  procedure mark_outbox_error(
    p_event_outbox_id      number,
    p_error_text           varchar2,
    p_retry_delay_minutes  number default 5,
    p_dead_letter          number default 0
  ) is
  begin
    update RRL_EVENT_OUTBOX
       set TRY_COUNT = nvl(TRY_COUNT, 0) + 1,
           STATUS = case
                      when nvl(p_dead_letter, 0) = 1 then 'DEAD_LETTER'
                      when nvl(TRY_COUNT, 0) + 1 >= nvl(MAX_TRY_COUNT, 10) then 'DEAD_LETTER'
                      else 'RETRY'
                    end,
           NEXT_RETRY_AT = case
                             when nvl(p_dead_letter, 0) = 1 then null
                             when nvl(TRY_COUNT, 0) + 1 >= nvl(MAX_TRY_COUNT, 10) then null
                             else sysdate + (nvl(p_retry_delay_minutes, 5) / 1440)
                           end,
           LAST_ERROR = substr(p_error_text, 1, 4000),
           FINISHED_AT = case
                           when nvl(p_dead_letter, 0) = 1 then sysdate
                           when nvl(TRY_COUNT, 0) + 1 >= nvl(MAX_TRY_COUNT, 10) then sysdate
                           else FINISHED_AT
                         end,
           LOCKED_BY = null,
           LOCKED_AT = null
     where EVENT_OUTBOX_ID = p_event_outbox_id;
  end mark_outbox_error;

  function add_adapter_request(
    p_system_code          varchar2,
    p_request_kind         varchar2,
    p_event_outbox_id      number default null,
    p_business_key         varchar2 default null,
    p_cert_alias           varchar2 default null,
    p_cert_thumbprint      varchar2 default null,
    p_signature_status     varchar2 default null,
    p_request_json         clob default null,
    p_status               varchar2 default 'STARTED',
    p_try_no               number default 1
  ) return number is
    v_id number;
  begin
    select RRL_ADAPTER_REQUEST_LOG_SQ.nextval into v_id from dual;

    insert into RRL_ADAPTER_REQUEST_LOG (
      ADAPTER_REQUEST_ID, EVENT_OUTBOX_ID, SYSTEM_CODE, REQUEST_KIND, BUSINESS_KEY,
      CERT_ALIAS, CERT_THUMBPRINT, SIGNATURE_STATUS, REQUEST_JSON, STATUS,
      TRY_NO, CREATED_AT, SENT_AT
    ) values (
      v_id, p_event_outbox_id, substr(upper(p_system_code), 1, 20),
      substr(upper(p_request_kind), 1, 80), substr(p_business_key, 1, 200),
      substr(p_cert_alias, 1, 200), substr(p_cert_thumbprint, 1, 200),
      substr(upper(p_signature_status), 1, 30), p_request_json,
      substr(upper(nvl(p_status, 'STARTED')), 1, 30), nvl(p_try_no, 1), sysdate, sysdate
    );

    return v_id;
  end add_adapter_request;

  procedure update_adapter_request(
    p_adapter_request_id   number,
    p_response_json        clob default null,
    p_external_request_id  varchar2 default null,
    p_external_document_id varchar2 default null,
    p_external_status      varchar2 default null,
    p_http_status          number default null,
    p_status               varchar2 default 'DONE',
    p_error_code           varchar2 default null,
    p_error_text           varchar2 default null
  ) is
  begin
    update RRL_ADAPTER_REQUEST_LOG
       set RESPONSE_JSON = p_response_json,
           EXTERNAL_REQUEST_ID = substr(p_external_request_id, 1, 200),
           EXTERNAL_DOCUMENT_ID = substr(p_external_document_id, 1, 200),
           EXTERNAL_STATUS = substr(p_external_status, 1, 50),
           HTTP_STATUS = p_http_status,
           STATUS = substr(upper(nvl(p_status, 'DONE')), 1, 30),
           ERROR_CODE = substr(p_error_code, 1, 100),
           ERROR_TEXT = substr(p_error_text, 1, 4000),
           FINISHED_AT = sysdate
     where ADAPTER_REQUEST_ID = p_adapter_request_id;
  end update_adapter_request;

  function create_quality_hold(
    p_entity_type      varchar2,
    p_entity_id        varchar2,
    p_reason_code      varchar2 default null,
    p_reason_text      varchar2 default null,
    p_created_by       varchar2 default null
  ) return number is
    v_id number;
  begin
    select RRL_QUALITY_HOLD_SQ.nextval into v_id from dual;

    insert into RRL_QUALITY_HOLD (
      QUALITY_HOLD_ID, ENTITY_TYPE, ENTITY_ID, HOLD_STATUS, REASON_CODE,
      REASON_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(upper(p_entity_type), 1, 50), substr(p_entity_id, 1, 100),
      'ACTIVE', substr(upper(p_reason_code), 1, 50), substr(p_reason_text, 1, 1000),
      sysdate, substr(p_created_by, 1, 50)
    );

    return v_id;
  end create_quality_hold;

  procedure release_quality_hold(
    p_quality_hold_id  number,
    p_released_by      varchar2 default null,
    p_release_reason   varchar2 default null
  ) is
  begin
    update RRL_QUALITY_HOLD
       set HOLD_STATUS = 'RELEASED',
           RELEASED_AT = sysdate,
           RELEASED_BY = substr(p_released_by, 1, 50),
           RELEASE_REASON = substr(p_release_reason, 1, 1000)
     where QUALITY_HOLD_ID = p_quality_hold_id
       and HOLD_STATUS = 'ACTIVE';
  end release_quality_hold;
end RRL_TRACEABILITY_API;
/
