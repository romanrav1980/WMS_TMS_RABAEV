prompt [migration 2026-05-17-003] Regulatory lifecycle entities - verify

select table_name
  from user_tables
 where table_name in (
   'RRL_MERCURY_SITE',
   'RRL_MERCURY_OPERATION',
   'RRL_REG_OPERATION_JOURNAL',
   'RRL_CRPT_CIRCULATION'
 )
 order by table_name;

select table_name, column_name
  from user_tab_columns
 where (table_name = 'RRL_PROD_BATCH' and column_name = 'MERCURY_SITE_ID')
    or (table_name = 'RRL_RAW_BATCH' and column_name = 'MERCURY_SITE_ID')
    or (table_name = 'RRL_MERCURY_BATCH' and column_name = 'MERCURY_SITE_ID')
    or (table_name = 'RRL_CRPT_CODES' and column_name in (
      'WITHDRAWN_AT',
      'INTRODUCTION_DOCUMENT_ID',
      'WITHDRAWAL_DOCUMENT_ID',
      'LAST_STATUS_AT',
      'LAST_ERROR'
    ))
 order by table_name, column_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_MERCURY_SITE_SQ',
   'RRL_MERCURY_OPERATION_SQ',
   'RRL_REG_OPERATION_JOURNAL_SQ',
   'RRL_CRPT_CIRCULATION_SQ'
 )
 order by sequence_name;

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_REGULATORY_API'
 order by object_type;

select name, type, line, position, text
  from user_errors
 where name = 'RRL_REGULATORY_API'
 order by sequence;

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;

prompt [migration 2026-05-17-003] Verify finished.
