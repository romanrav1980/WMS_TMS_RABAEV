prompt [migration 2026-05-17-001] Feed factory traceability base - rollback
prompt WARNING: this script drops new migration objects and columns. Export data first if the migration was used.

declare
  procedure drop_index_if_exists(p_name varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n > 0 then
      execute immediate 'drop index ' || p_name;
    end if;
  exception
    when others then
      if sqlcode != -1418 then raise; end if;
  end;

  procedure drop_table_if_exists(p_name varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
    if n > 0 then
      execute immediate 'drop table ' || p_name || ' cascade constraints';
    end if;
  end;

  procedure drop_sequence_if_exists(p_name varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n > 0 then
      execute immediate 'drop sequence ' || p_name;
    end if;
  end;

  procedure drop_column_if_exists(p_table varchar2, p_column varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n > 0 then
      execute immediate 'alter table ' || p_table || ' drop column ' || p_column;
    end if;
  end;
begin
  drop_index_if_exists('RRL_PALLETS_I_PROD_BATCH');
  drop_index_if_exists('RRL_PALLETS_I_SSCC');
  drop_index_if_exists('RRL_SB_PAL_ROWS_I_PROD_BATCH');

  drop_column_if_exists('RRL_SBORKA_PALLET_ROWS', 'CRPT_TRANSFER_MODE');
  drop_column_if_exists('RRL_SBORKA_PALLET_ROWS', 'SSCC');
  drop_column_if_exists('RRL_SBORKA_PALLET_ROWS', 'PROD_BATCH_ID');

  drop_column_if_exists('RRL_PALLETS', 'QUALITY_STATUS');
  drop_column_if_exists('RRL_PALLETS', 'CRPT_STATUS');
  drop_column_if_exists('RRL_PALLETS', 'MERCURY_STATUS');
  drop_column_if_exists('RRL_PALLETS', 'SSCC');
  drop_column_if_exists('RRL_PALLETS', 'PROD_BATCH_ID');

  drop_table_if_exists('RRL_FILE_EXCHANGE_LOG');
  drop_table_if_exists('RRL_REGULATORY_OUTBOX');
  drop_table_if_exists('RRL_CRPT_AGGREGATION_ITEMS');
  drop_table_if_exists('RRL_CRPT_AGGREGATION');
  drop_table_if_exists('RRL_CRPT_CODES');
  drop_table_if_exists('RRL_MERCURY_BATCH');
  drop_table_if_exists('RRL_PROD_RAW_USAGE');
  drop_table_if_exists('RRL_RAW_BATCH');
  drop_table_if_exists('RRL_PROD_BATCH_PALLETS');
  drop_table_if_exists('RRL_PROD_BATCH');
  drop_table_if_exists('RRL_CLIENT_REG_PROFILE');

  delete from RRL_SYSTEM_SETTINGS
   where SETTING_KEY in ('PRODUCTION_BATCH_SOURCE', 'PROD_EXCHANGE_ROOT_DIR', 'PROD_EXCHANGE_ENABLED');

  delete from RRL_SCHEMA_MIGRATIONS
   where MIGRATION_ID = '2026-05-17-001-feed-factory-traceability';

  drop_sequence_if_exists('RRL_FILE_EXCHANGE_LOG_SQ');
  drop_sequence_if_exists('RRL_REGULATORY_OUTBOX_SQ');
  drop_sequence_if_exists('RRL_CRPT_AGGREGATION_SQ');
  drop_sequence_if_exists('RRL_CRPT_CODES_SQ');
  drop_sequence_if_exists('RRL_PROD_RAW_USAGE_SQ');
  drop_sequence_if_exists('RRL_RAW_BATCH_SQ');
  drop_sequence_if_exists('RRL_PROD_BATCH_SQ');
end;
/

commit;

prompt [migration 2026-05-17-001] Rollback finished. Run 001_verify.sql.

