prompt [migration 2026-05-17-004] API audit and replay - verify

select table_name
  from user_tables
 where table_name = 'RRL_API_CALL_LOG';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_API_CALL_LOG_SQ';

select column_name
  from user_tab_columns
 where table_name = 'RRL_API_CALL_LOG'
   and column_name in (
    'API_CALL_ID',
    'REQUEST_ID',
    'REPLAY_OF_CALL_ID',
    'METHOD',
    'PATH',
    'REQUEST_BODY',
    'RESPONSE_BODY',
    'STATUS',
    'REPLAYABLE',
    'REPLAY_COUNT',
    'LAST_REPLAY_ERROR',
    'LOCAL_LOG_PATH'
   )
 order by column_name;

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_API_AUDIT_API'
 order by object_type;

select name, type, line, position, text
  from user_errors
 where name = 'RRL_API_AUDIT_API'
 order by sequence;

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;

prompt [migration 2026-05-17-004] Verify finished.
