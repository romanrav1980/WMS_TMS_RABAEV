-- 2026-05-17-010-article-code-length-40
-- Widen legacy WMS/MES article/material code columns to SAP/S4-compatible 40 characters.
-- This migration is additive/safe: it only increases VARCHAR2 lengths and does not delete data.

declare
  procedure widen_varchar2(
    p_table_name in varchar2,
    p_column_name in varchar2,
    p_target_len in number
  ) is
    v_data_type user_tab_columns.data_type%type;
    v_data_len user_tab_columns.data_length%type;
    v_char_len user_tab_columns.char_length%type;
    v_char_used user_tab_columns.char_used%type;
    v_current_len number;
    v_semantics varchar2(10);
  begin
    select data_type, data_length, char_length, char_used
      into v_data_type, v_data_len, v_char_len, v_char_used
      from user_tab_columns
     where table_name = upper(p_table_name)
       and column_name = upper(p_column_name);

    if v_data_type <> 'VARCHAR2' then
      raise_application_error(-21010, p_table_name || '.' || p_column_name || ' is not VARCHAR2.');
    end if;

    v_current_len := case when v_char_used = 'C' then v_char_len else v_data_len end;
    v_semantics := case when v_char_used = 'C' then ' char' else '' end;

    if v_current_len < p_target_len then
      execute immediate
        'alter table ' || dbms_assert.simple_sql_name(upper(p_table_name)) ||
        ' modify (' || dbms_assert.simple_sql_name(upper(p_column_name)) ||
        ' varchar2(' || to_char(p_target_len) || v_semantics || '))';
    end if;
  exception
    when no_data_found then
      raise_application_error(-21011, p_table_name || '.' || p_column_name || ' was not found.');
  end widen_varchar2;
begin
  -- Legacy article master and article modifiers.
  widen_varchar2('RRL_ARTICULS', 'ACTICUL', 40);
  widen_varchar2('RRL_ARTICUL_MODS', 'ARTICUL', 40);
  widen_varchar2('RRL_WARES', 'FAKE_ART', 40);

  -- BOM and MES traceability entities.
  widen_varchar2('RRL_BOM', 'TARGET_ARTICUL', 40);
  widen_varchar2('RRL_BOM_LINE', 'COMPONENT_ARTICUL', 40);
  widen_varchar2('RRL_PROD_BATCH', 'ARTICUL', 40);
  widen_varchar2('RRL_PROD_RAW_USAGE', 'RAW_ARTICUL', 40);
  widen_varchar2('RRL_RAW_BATCH', 'ARTICUL', 40);

  -- Legacy WMS documents, pallets, picking and temporary rows.
  widen_varchar2('RRL_ORDER_PALLET_ROWS', 'ARTICUL', 40);
  widen_varchar2('RRL_ORDER_ROWS', 'ARTICUL', 40);
  widen_varchar2('RRL_OTHOD_NAKLAD_ROWS', 'ARTICUL', 40);
  widen_varchar2('RRL_PALLETS', 'ARTICUL', 40);
  widen_varchar2('RRL_PRIHOD_NAKLAD_ROWS', 'ARTICUL', 40);
  widen_varchar2('RRL_SBORKA_PALLET_ROWS', 'ARTICUL', 40);
  widen_varchar2('TMP_PALLET_ROWS', 'ARTICUL', 40);
end;
/

declare
  v_sql varchar2(32767);
begin
  for r in (
    select text
      from user_source
     where name = 'RRL_BOM_API'
       and type = 'PACKAGE BODY'
     order by line
  ) loop
    v_sql := v_sql || r.text;
  end loop;

  if v_sql is null then
    raise_application_error(-21012, 'RRL_BOM_API package body source was not found.');
  end if;

  v_sql := 'create or replace ' || v_sql;

  v_sql := replace(
    v_sql,
    'substr(upper(trim(p_target_articul)), 1, 15)',
    'substr(upper(trim(p_target_articul)), 1, 40)'
  );
  v_sql := replace(
    v_sql,
    'substr(upper(trim(p_component_articul)), 1, 15)',
    'substr(upper(trim(p_component_articul)), 1, 40)'
  );

  execute immediate v_sql;
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-010-article-code-length-40' MIGRATION_ID,
         'Widen article/material code columns to 40 chars for SAP/S4 compatibility' DESCRIPTION,
         '010_apply.sql' SCRIPT_NAME,
         '010_rollback.sql' ROLLBACK_SCRIPT
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');
