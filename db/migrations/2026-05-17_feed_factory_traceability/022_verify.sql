prompt [migration 2026-05-17-022] Slow SQL diagnostics - verify

select table_name
  from user_tables
 where table_name = 'RRL_SQL_SLOW_LOG';

select sequence_name
  from user_sequences
 where sequence_name = 'RRL_SQL_SLOW_LOG_SQ';

select count(*) SLOW_SQL_INDEX_COUNT
  from user_indexes
 where index_name in (
   'RRL_SQL_SLOW_LOG_I1',
   'RRL_SQL_SLOW_LOG_I2',
   'RRL_SQL_SLOW_LOG_I3',
   'RRL_SQL_SLOW_LOG_I4',
   'RRL_SQL_SLOW_LOG_I5'
 );

select count(*) SLOW_SQL_RIGHT_COUNT
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) = 'SLOW_SQL_VIEW';

select count(*) INVALID_CNT
  from user_objects
 where status <> 'VALID'
   and object_type in ('PACKAGE', 'PACKAGE BODY', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW');

prompt [migration 2026-05-17-022] verify done
