prompt [migration 2026-05-17-012] WMS warehouse settings - verify

select column_name, data_type, data_length, nullable
  from user_tab_columns
 where table_name = 'RRL_WARES'
   and column_name in (
     'FLAG_RAW_MATERIAL',
     'FLAG_PRODUCTION',
     'FLAG_PRODUCTION_BUFFER',
     'FLAG_FINISHED_GOODS',
     'MES_ENABLED',
     'DEFAULT_RECEIVE_CELL',
     'DEFAULT_ISSUE_CELL',
     'WARE_COMMENT'
   )
 order by column_name;

select 'GLOBAL_ADMIN_WAREHOUSE_RIGHTS' check_name,
       count(*) actual_count
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in ('WAREHOUSE_SETTINGS_VIEW', 'WAREHOUSE_SETTINGS_EDIT');

select 'WAREHOUSE_SEED_MOJIBAKE_MARKERS' check_name,
       count(*) actual_count
  from (
        select WARE_COMMENT text_value
          from RRL_WARES
         where ID between 9101 and 9104
        union all
        select NAME text_value
          from RRL_ARTICULS
         where ACTICUL like 'RM-%'
       )
 where text_value like '%' || unistr('\0420\045E') || '%'
    or text_value like '%' || unistr('\0420\045F') || '%'
    or text_value like '%' || unistr('\0421\0403') || '%'
    or text_value like '%' || unistr('\0420\045C') || '%'
    or text_value like '%' || unistr('\0420\0403') || '%'
    or text_value like '%' || unistr('\0421\0453') || '%'
    or text_value like '%' || unistr('\0421\2039') || '%'
    or text_value like '%' || unistr('\0421\040F') || '%';

select object_name, object_type, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
