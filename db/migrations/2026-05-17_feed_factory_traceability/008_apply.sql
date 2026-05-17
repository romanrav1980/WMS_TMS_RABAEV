prompt [migration 2026-05-17-008] Traceability spine and event outbox - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_table('RRL_TRACE_EVENT', q'[
    create table RRL_TRACE_EVENT (
      TRACE_EVENT_ID number not null,
      EVENT_TYPE varchar2(80) not null,
      ENTITY_TYPE varchar2(50) not null,
      ENTITY_ID varchar2(100) not null,
      SOURCE_SYSTEM varchar2(30),
      CORRELATION_ID varchar2(100),
      IDEMPOTENCY_KEY varchar2(100),
      PAYLOAD_JSON clob,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_TRACE_EVENT_PK primary key (TRACE_EVENT_ID),
      constraint RRL_TRACE_EVENT_U1 unique (IDEMPOTENCY_KEY)
    )
  ]');

  ensure_table('RRL_TRACE_EDGE', q'[
    create table RRL_TRACE_EDGE (
      TRACE_EDGE_ID number not null,
      FROM_ENTITY_TYPE varchar2(50) not null,
      FROM_ENTITY_ID varchar2(100) not null,
      TO_ENTITY_TYPE varchar2(50) not null,
      TO_ENTITY_ID varchar2(100) not null,
      EDGE_TYPE varchar2(50) not null,
      QUANTITY number,
      UNIT_CODE varchar2(20),
      TRACE_EVENT_ID number,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_TRACE_EDGE_PK primary key (TRACE_EDGE_ID),
      constraint RRL_TRACE_EDGE_FK1 foreign key (TRACE_EVENT_ID)
        references RRL_TRACE_EVENT (TRACE_EVENT_ID)
    )
  ]');

  ensure_table('RRL_EVENT_OUTBOX', q'[
    create table RRL_EVENT_OUTBOX (
      EVENT_OUTBOX_ID number not null,
      EVENT_TYPE varchar2(80) not null,
      AGGREGATE_TYPE varchar2(50) not null,
      AGGREGATE_ID varchar2(100) not null,
      TARGET_SYSTEM varchar2(30),
      CORRELATION_ID varchar2(100),
      IDEMPOTENCY_KEY varchar2(100) not null,
      PAYLOAD_JSON clob not null,
      STATUS varchar2(30) default 'PENDING' not null,
      TRY_COUNT number default 0 not null,
      MAX_TRY_COUNT number default 10 not null,
      NEXT_RETRY_AT date,
      LOCKED_BY varchar2(100),
      LOCKED_AT date,
      LAST_ERROR varchar2(4000),
      CREATED_AT date default sysdate not null,
      SENT_AT date,
      FINISHED_AT date,
      CANCELLED_AT date,
      constraint RRL_EVENT_OUTBOX_PK primary key (EVENT_OUTBOX_ID),
      constraint RRL_EVENT_OUTBOX_U1 unique (IDEMPOTENCY_KEY),
      constraint RRL_EVENT_OUTBOX_CHK1 check (STATUS in (
        'PENDING', 'LOCKED', 'SENT', 'DONE', 'RETRY', 'ERROR',
        'DEAD_LETTER', 'CANCELLED_BY_OPERATOR'
      ))
    )
  ]');

  ensure_table('RRL_ADAPTER_REQUEST_LOG', q'[
    create table RRL_ADAPTER_REQUEST_LOG (
      ADAPTER_REQUEST_ID number not null,
      EVENT_OUTBOX_ID number,
      SYSTEM_CODE varchar2(20) not null,
      REQUEST_KIND varchar2(80) not null,
      BUSINESS_KEY varchar2(200),
      CERT_ALIAS varchar2(200),
      CERT_THUMBPRINT varchar2(200),
      SIGNATURE_STATUS varchar2(30),
      REQUEST_JSON clob,
      RESPONSE_JSON clob,
      EXTERNAL_REQUEST_ID varchar2(200),
      EXTERNAL_DOCUMENT_ID varchar2(200),
      EXTERNAL_STATUS varchar2(50),
      HTTP_STATUS number,
      STATUS varchar2(30) not null,
      ERROR_CODE varchar2(100),
      ERROR_TEXT varchar2(4000),
      TRY_NO number default 1 not null,
      CREATED_AT date default sysdate not null,
      SENT_AT date,
      FINISHED_AT date,
      constraint RRL_ADAPTER_REQ_PK primary key (ADAPTER_REQUEST_ID),
      constraint RRL_ADAPTER_REQ_FK1 foreign key (EVENT_OUTBOX_ID)
        references RRL_EVENT_OUTBOX (EVENT_OUTBOX_ID)
    )
  ]');

  ensure_table('RRL_QUALITY_HOLD', q'[
    create table RRL_QUALITY_HOLD (
      QUALITY_HOLD_ID number not null,
      ENTITY_TYPE varchar2(50) not null,
      ENTITY_ID varchar2(100) not null,
      HOLD_STATUS varchar2(30) default 'ACTIVE' not null,
      REASON_CODE varchar2(50),
      REASON_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      RELEASED_AT date,
      RELEASED_BY varchar2(50),
      RELEASE_REASON varchar2(1000),
      constraint RRL_QUALITY_HOLD_PK primary key (QUALITY_HOLD_ID),
      constraint RRL_QUALITY_HOLD_CHK1 check (HOLD_STATUS in ('ACTIVE', 'RELEASED', 'CANCELLED'))
    )
  ]');

  ensure_sequence('RRL_TRACE_EVENT_SQ', 'create sequence RRL_TRACE_EVENT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TRACE_EDGE_SQ', 'create sequence RRL_TRACE_EDGE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_EVENT_OUTBOX_SQ', 'create sequence RRL_EVENT_OUTBOX_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_ADAPTER_REQUEST_LOG_SQ', 'create sequence RRL_ADAPTER_REQUEST_LOG_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_QUALITY_HOLD_SQ', 'create sequence RRL_QUALITY_HOLD_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_TRACE_EVENT_I1', 'create index RRL_TRACE_EVENT_I1 on RRL_TRACE_EVENT (ENTITY_TYPE, ENTITY_ID, CREATED_AT)');
  ensure_index('RRL_TRACE_EVENT_I2', 'create index RRL_TRACE_EVENT_I2 on RRL_TRACE_EVENT (CORRELATION_ID, TRACE_EVENT_ID)');
  ensure_index('RRL_TRACE_EDGE_I1', 'create index RRL_TRACE_EDGE_I1 on RRL_TRACE_EDGE (FROM_ENTITY_TYPE, FROM_ENTITY_ID)');
  ensure_index('RRL_TRACE_EDGE_I2', 'create index RRL_TRACE_EDGE_I2 on RRL_TRACE_EDGE (TO_ENTITY_TYPE, TO_ENTITY_ID)');
  ensure_index('RRL_TRACE_EDGE_I3', 'create index RRL_TRACE_EDGE_I3 on RRL_TRACE_EDGE (TRACE_EVENT_ID)');
  ensure_index('RRL_EVENT_OUTBOX_I1', 'create index RRL_EVENT_OUTBOX_I1 on RRL_EVENT_OUTBOX (STATUS, NEXT_RETRY_AT, EVENT_OUTBOX_ID)');
  ensure_index('RRL_EVENT_OUTBOX_I2', 'create index RRL_EVENT_OUTBOX_I2 on RRL_EVENT_OUTBOX (TARGET_SYSTEM, STATUS, EVENT_OUTBOX_ID)');
  ensure_index('RRL_EVENT_OUTBOX_I3', 'create index RRL_EVENT_OUTBOX_I3 on RRL_EVENT_OUTBOX (AGGREGATE_TYPE, AGGREGATE_ID)');
  ensure_index('RRL_ADAPTER_REQ_I1', 'create index RRL_ADAPTER_REQ_I1 on RRL_ADAPTER_REQUEST_LOG (EVENT_OUTBOX_ID, ADAPTER_REQUEST_ID)');
  ensure_index('RRL_ADAPTER_REQ_I2', 'create index RRL_ADAPTER_REQ_I2 on RRL_ADAPTER_REQUEST_LOG (SYSTEM_CODE, STATUS, CREATED_AT)');
  ensure_index('RRL_QUALITY_HOLD_I1', 'create index RRL_QUALITY_HOLD_I1 on RRL_QUALITY_HOLD (ENTITY_TYPE, ENTITY_ID, HOLD_STATUS)');
end;
/

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

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'TRACEABILITY_VIEW' RIGHT1, 'View traceability genealogy' DESCR from dual
    union all
    select 'EXTERNAL_OUTBOX_VIEW', 'View external outbox and adapter request journal' from dual
    union all
    select 'EXTERNAL_OUTBOX_RETRY', 'Retry external outbox events' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-008-traceability-spine-outbox' migration_id,
         'Traceability events, genealogy edges, durable event outbox, adapter request log, and QA hold' description,
         '008_apply.sql' script_name,
         '008_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-008] Apply finished. Run 008_verify.sql.
