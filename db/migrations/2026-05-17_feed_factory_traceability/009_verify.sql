-- 2026-05-17-009-bom-production-block verification

select 'TABLES' check_name,
       count(*) rows_found
  from user_tables
 where table_name in (
   'RRL_BOM',
   'RRL_BOM_LINE',
   'RRL_BOM_AUDIT'
 );

select 'SEQUENCES' check_name,
       count(*) rows_found
  from user_sequences
 where sequence_name in (
   'RRL_BOM_SQ',
   'RRL_BOM_LINE_SQ',
   'RRL_BOM_AUDIT_SQ'
 );

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_BOM_API'
 order by object_type;

select 'MIGRATION_LEDGER' check_name,
       count(*) rows_found
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-009-bom-production-block';

select 'GLOBAL_ADMIN_RIGHTS' check_name,
       count(*) rows_found
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'BOM_VIEW',
     'BOM_EDIT',
     'BOM_APPROVE',
     'BOM_BLOCK',
     'BOM_MAKE_PRIMARY',
     'BOM_USE_ALTERNATIVE'
   );

select table_name, count(*) column_count
  from user_tab_columns
 where table_name in (
   'RRL_BOM',
   'RRL_BOM_LINE',
   'RRL_BOM_AUDIT'
 )
 group by table_name
 order by table_name;

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
