prompt [migration 2026-05-17-004] API audit and replay - apply

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

  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate 'alter table ' || p_table || ' add (' || p_sql || ')';
    end if;
  end;
begin
  ensure_table('RRL_API_CALL_LOG', q'[
    create table RRL_API_CALL_LOG (
      API_CALL_ID number not null,
      REQUEST_ID varchar2(64) not null,
      REPLAY_OF_CALL_ID number,
      REPLAY_RUN_ID varchar2(64),
      METHOD varchar2(12) not null,
      PATH varchar2(1000) not null,
      QUERY_STRING varchar2(4000),
      URL varchar2(4000),
      CLIENT_IP varchar2(100),
      USER_AGENT varchar2(1000),
      REQUEST_HEADERS_JSON clob,
      REQUEST_BODY clob,
      REQUEST_BODY_SHA256 varchar2(64),
      REQUEST_BODY_TRUNCATED number(1) default 0 not null,
      RESPONSE_STATUS number,
      RESPONSE_HEADERS_JSON clob,
      RESPONSE_BODY clob,
      RESPONSE_BODY_TRUNCATED number(1) default 0 not null,
      ERROR_TEXT varchar2(4000),
      STATUS varchar2(30) default 'STARTED' not null,
      REPLAYABLE number(1) default 1 not null,
      REPLAY_COUNT number default 0 not null,
      LAST_REPLAY_AT date,
      LAST_REPLAY_CALL_ID number,
      LAST_REPLAY_ERROR varchar2(4000),
      LOCAL_LOG_PATH varchar2(1024),
      STARTED_AT date default sysdate not null,
      FINISHED_AT date,
      DURATION_MS number,
      CREATED_AT date default sysdate,
      constraint RRL_API_CALL_LOG_PK primary key (API_CALL_ID),
      constraint RRL_API_CALL_LOG_U1 unique (REQUEST_ID)
    )
  ]');

  ensure_sequence('RRL_API_CALL_LOG_SQ', 'create sequence RRL_API_CALL_LOG_SQ start with 1 increment by 1 nocache');

  ensure_column('RRL_API_CALL_LOG', 'LAST_REPLAY_ERROR', 'LAST_REPLAY_ERROR varchar2(4000)');

  ensure_index('RRL_API_CALL_LOG_I1', 'create index RRL_API_CALL_LOG_I1 on RRL_API_CALL_LOG (STARTED_AT, API_CALL_ID)');
  ensure_index('RRL_API_CALL_LOG_I2', 'create index RRL_API_CALL_LOG_I2 on RRL_API_CALL_LOG (STATUS, STARTED_AT)');
  ensure_index('RRL_API_CALL_LOG_I3', 'create index RRL_API_CALL_LOG_I3 on RRL_API_CALL_LOG (METHOD, PATH)');
  ensure_index('RRL_API_CALL_LOG_I4', 'create index RRL_API_CALL_LOG_I4 on RRL_API_CALL_LOG (REPLAY_OF_CALL_ID)');
end;
/

create or replace package RRL_API_AUDIT_API as
  function start_call(
    p_request_id             varchar2,
    p_replay_of_call_id      number default null,
    p_replay_run_id          varchar2 default null,
    p_method                 varchar2,
    p_path                   varchar2,
    p_query_string           varchar2 default null,
    p_url                    varchar2 default null,
    p_client_ip              varchar2 default null,
    p_user_agent             varchar2 default null,
    p_request_headers_json   clob default null,
    p_request_body           clob default null,
    p_request_body_sha256    varchar2 default null,
    p_request_body_truncated number default 0,
    p_replayable             number default 1,
    p_local_log_path         varchar2 default null
  ) return number;

  procedure finish_call(
    p_api_call_id            number,
    p_response_status        number default null,
    p_response_headers_json  clob default null,
    p_response_body          clob default null,
    p_response_body_truncated number default 0,
    p_error_text             varchar2 default null,
    p_status                 varchar2 default 'DONE',
    p_duration_ms            number default null,
    p_local_log_path         varchar2 default null
  );

  procedure mark_replay_result(
    p_source_call_id         number,
    p_replay_call_id         number default null,
    p_error_text             varchar2 default null
  );
end RRL_API_AUDIT_API;
/

create or replace package body RRL_API_AUDIT_API as
  function start_call(
    p_request_id             varchar2,
    p_replay_of_call_id      number default null,
    p_replay_run_id          varchar2 default null,
    p_method                 varchar2,
    p_path                   varchar2,
    p_query_string           varchar2 default null,
    p_url                    varchar2 default null,
    p_client_ip              varchar2 default null,
    p_user_agent             varchar2 default null,
    p_request_headers_json   clob default null,
    p_request_body           clob default null,
    p_request_body_sha256    varchar2 default null,
    p_request_body_truncated number default 0,
    p_replayable             number default 1,
    p_local_log_path         varchar2 default null
  ) return number is
    v_id number;
  begin
    begin
      select API_CALL_ID
        into v_id
        from RRL_API_CALL_LOG
       where REQUEST_ID = p_request_id;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_API_CALL_LOG_SQ.nextval into v_id from dual;

    insert into RRL_API_CALL_LOG (
      API_CALL_ID, REQUEST_ID, REPLAY_OF_CALL_ID, REPLAY_RUN_ID,
      METHOD, PATH, QUERY_STRING, URL, CLIENT_IP, USER_AGENT,
      REQUEST_HEADERS_JSON, REQUEST_BODY, REQUEST_BODY_SHA256,
      REQUEST_BODY_TRUNCATED, STATUS, REPLAYABLE, LOCAL_LOG_PATH, STARTED_AT, CREATED_AT
    ) values (
      v_id, p_request_id, p_replay_of_call_id, p_replay_run_id,
      upper(p_method), substr(p_path, 1, 1000), substr(p_query_string, 1, 4000), substr(p_url, 1, 4000),
      substr(p_client_ip, 1, 100), substr(p_user_agent, 1, 1000),
      p_request_headers_json, p_request_body, p_request_body_sha256,
      nvl(p_request_body_truncated, 0), 'STARTED', nvl(p_replayable, 1), p_local_log_path, sysdate, sysdate
    );

    return v_id;
  end start_call;

  procedure finish_call(
    p_api_call_id            number,
    p_response_status        number default null,
    p_response_headers_json  clob default null,
    p_response_body          clob default null,
    p_response_body_truncated number default 0,
    p_error_text             varchar2 default null,
    p_status                 varchar2 default 'DONE',
    p_duration_ms            number default null,
    p_local_log_path         varchar2 default null
  ) is
  begin
    update RRL_API_CALL_LOG
       set RESPONSE_STATUS = p_response_status,
           RESPONSE_HEADERS_JSON = p_response_headers_json,
           RESPONSE_BODY = p_response_body,
           RESPONSE_BODY_TRUNCATED = nvl(p_response_body_truncated, 0),
           ERROR_TEXT = substr(p_error_text, 1, 4000),
           STATUS = nvl(p_status, 'DONE'),
           FINISHED_AT = sysdate,
           DURATION_MS = p_duration_ms,
           LOCAL_LOG_PATH = nvl(p_local_log_path, LOCAL_LOG_PATH)
     where API_CALL_ID = p_api_call_id;
  end finish_call;

  procedure mark_replay_result(
    p_source_call_id         number,
    p_replay_call_id         number default null,
    p_error_text             varchar2 default null
  ) is
  begin
    update RRL_API_CALL_LOG
       set REPLAY_COUNT = nvl(REPLAY_COUNT, 0) + 1,
           LAST_REPLAY_AT = sysdate,
           LAST_REPLAY_CALL_ID = nvl(p_replay_call_id, LAST_REPLAY_CALL_ID),
           LAST_REPLAY_ERROR = substr(p_error_text, 1, 4000)
     where API_CALL_ID = p_source_call_id;
  end mark_replay_result;
end RRL_API_AUDIT_API;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-004-api-audit-replay' migration_id,
         'API call audit log with local/Oracle replay support' description,
         '004_apply.sql' script_name,
         '004_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-004] Apply finished. Run 004_verify.sql.
