-- 2026-05-17-010-article-code-length-40 verification

select table_name,
       column_name,
       data_type,
       data_length,
       char_length,
       char_used
  from user_tab_columns
 where table_name not like 'BIN$%'
   and (
     (table_name, column_name) in (
       ('RRL_ARTICULS', 'ACTICUL'),
       ('RRL_ARTICUL_MODS', 'ARTICUL'),
       ('RRL_WARES', 'FAKE_ART'),
       ('RRL_BOM', 'TARGET_ARTICUL'),
       ('RRL_BOM_LINE', 'COMPONENT_ARTICUL'),
       ('RRL_PROD_BATCH', 'ARTICUL'),
       ('RRL_PROD_RAW_USAGE', 'RAW_ARTICUL'),
       ('RRL_RAW_BATCH', 'ARTICUL'),
       ('RRL_ORDER_PALLET_ROWS', 'ARTICUL'),
       ('RRL_ORDER_ROWS', 'ARTICUL'),
       ('RRL_OTHOD_NAKLAD_ROWS', 'ARTICUL'),
       ('RRL_PALLETS', 'ARTICUL'),
       ('RRL_PRIHOD_NAKLAD_ROWS', 'ARTICUL'),
       ('RRL_SBORKA_PALLET_ROWS', 'ARTICUL'),
       ('TMP_PALLET_ROWS', 'ARTICUL')
     )
   )
 order by table_name, column_name;

select 'ARTICLE_COLUMNS_BELOW_40' check_name,
       count(*) rows_found
  from user_tab_columns
 where table_name not like 'BIN$%'
   and data_type = 'VARCHAR2'
   and (
     upper(column_name) like '%ARTICUL%'
     or upper(column_name) like '%ACTICUL%'
     or upper(column_name) = 'FAKE_ART'
   )
   and case when char_used = 'C' then char_length else data_length end < 40;

select 'MIGRATION_LEDGER' check_name,
       count(*) rows_found
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-010-article-code-length-40';

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
