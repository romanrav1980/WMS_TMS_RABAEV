prompt [migration 2026-05-17-004] Smoke with cleanup

declare
  v_call_id number;
begin
  v_call_id := RRL_API_AUDIT_API.start_call(
    p_request_id => 'SMOKE-API-CALL-004',
    p_method => 'POST',
    p_path => '/api/smoke',
    p_query_string => 'x=1',
    p_url => 'http://127.0.0.1:8088/api/smoke?x=1',
    p_client_ip => '127.0.0.1',
    p_user_agent => 'smoke',
    p_request_headers_json => '{"x-smoke":"1"}',
    p_request_body => '{"smoke":true}',
    p_request_body_sha256 => 'SMOKE',
    p_replayable => 1,
    p_local_log_path => 'runtime/api_audit/smoke.jsonl'
  );

  RRL_API_AUDIT_API.finish_call(
    p_api_call_id => v_call_id,
    p_response_status => 200,
    p_response_headers_json => '{"content-type":"application/json"}',
    p_response_body => '{"ok":true}',
    p_status => 'DONE',
    p_duration_ms => 12,
    p_local_log_path => 'runtime/api_audit/smoke.jsonl'
  );

  RRL_API_AUDIT_API.mark_replay_result(
    p_source_call_id => v_call_id,
    p_replay_call_id => null
  );

  if v_call_id is null then
    raise_application_error(-20004, 'RRL_API_AUDIT_API smoke failed.');
  end if;
end;
/

delete from RRL_API_CALL_LOG
 where REQUEST_ID = 'SMOKE-API-CALL-004';

commit;

select 'SMOKE-API-CALL-004' check_name, count(*) rows_left
  from RRL_API_CALL_LOG
 where REQUEST_ID = 'SMOKE-API-CALL-004';

prompt [migration 2026-05-17-004] Smoke with cleanup finished.
