prompt [migration 2026-05-17-001] Feed factory traceability base - apply

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

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_table('RRL_SCHEMA_MIGRATIONS', q'[
    create table RRL_SCHEMA_MIGRATIONS (
      MIGRATION_ID varchar2(100) not null,
      DESCRIPTION varchar2(500),
      APPLIED_AT date default sysdate not null,
      APPLIED_BY varchar2(100) default user,
      SCRIPT_NAME varchar2(255),
      ROLLBACK_SCRIPT varchar2(255),
      STATUS varchar2(30) default 'APPLIED' not null,
      NOTES varchar2(4000),
      constraint RRL_SCHEMA_MIGRATIONS_PK primary key (MIGRATION_ID)
    )
  ]');

  ensure_table('RRL_SYSTEM_SETTINGS', q'[
    create table RRL_SYSTEM_SETTINGS (
      SETTING_KEY varchar2(100) not null,
      SETTING_VALUE varchar2(4000),
      DESCRIPTION varchar2(1000),
      UPDATED_AT date default sysdate,
      UPDATED_BY varchar2(100),
      constraint RRL_SYSTEM_SETTINGS_PK primary key (SETTING_KEY)
    )
  ]');

  ensure_table('RRL_CLIENT_REG_PROFILE', q'[
    create table RRL_CLIENT_REG_PROFILE (
      CLIENT_ID varchar2(100) not null,
      CLIENT_NAME varchar2(255),
      INN varchar2(20),
      KPP varchar2(20),
      GLN varchar2(32),
      ACCEPTS_CRPT_AGGREGATION number(1) default 0 not null,
      CRPT_ACCEPTANCE_MODE varchar2(20) default 'ITEM_CODES' not null,
      REQUIRES_MERCURY_VSD number(1) default 0 not null,
      EDI_CHANNEL varchar2(50),
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate,
      UPDATED_AT date,
      constraint RRL_CLIENT_REG_PROFILE_PK primary key (CLIENT_ID),
      constraint RRL_CLIENT_REG_PROFILE_M1 check (CRPT_ACCEPTANCE_MODE in ('ITEM_CODES', 'SSCC', 'MIXED'))
    )
  ]');

  ensure_table('RRL_PROD_BATCH', q'[
    create table RRL_PROD_BATCH (
      PROD_BATCH_ID number not null,
      PROD_BATCH_NO varchar2(100) not null,
      PRODUCTION_ORDER_ID number,
      SOURCE_SYSTEM varchar2(100),
      SOURCE_MESSAGE_ID varchar2(100),
      EXTERNAL_OPERATION_ID varchar2(100),
      EXTERNAL_BATCH_ID varchar2(100),
      ARTICUL varchar2(40),
      MOD_ID number,
      GTIN varchar2(14),
      PRODUCT_NAME varchar2(255),
      PRODUCED_DATE_FROM date,
      PRODUCED_DATE_TO date,
      EXPIRY_DATE_FROM date,
      EXPIRY_DATE_TO date,
      TOTAL_QUANTITY number,
      TOTAL_PACK_COUNT number,
      UNIT_CODE varchar2(20),
      WARE_ID number,
      PRODUCTION_LINE varchar2(100),
      SHIFT_ID varchar2(100),
      QUALITY_STATUS varchar2(30) default 'DRAFT',
      MERCURY_REQUIRED number(1) default 0 not null,
      CRPT_REQUIRED number(1) default 0 not null,
      MERCURY_STATUS varchar2(30) default 'NOT_REQUIRED',
      CRPT_STATUS varchar2(30) default 'NOT_REQUIRED',
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PROD_BATCH_PK primary key (PROD_BATCH_ID),
      constraint RRL_PROD_BATCH_U1 unique (PROD_BATCH_NO, ARTICUL, WARE_ID),
      constraint RRL_PROD_BATCH_U2 unique (SOURCE_SYSTEM, SOURCE_MESSAGE_ID, EXTERNAL_BATCH_ID)
    )
  ]');

  ensure_table('RRL_PROD_BATCH_PALLETS', q'[
    create table RRL_PROD_BATCH_PALLETS (
      PROD_BATCH_ID number not null,
      UID_PALLET varchar2(50) not null,
      PALLET_NO number,
      QUANTITY number,
      PACK_COUNT number,
      NET_WEIGHT number,
      GROSS_WEIGHT number,
      SSCC varchar2(32),
      AGGREGATION_STATUS varchar2(30),
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(50),
      constraint RRL_PROD_BATCH_PALLETS_PK primary key (PROD_BATCH_ID, UID_PALLET)
    )
  ]');

  ensure_table('RRL_RAW_BATCH', q'[
    create table RRL_RAW_BATCH (
      RAW_BATCH_ID number not null,
      RAW_BATCH_NO varchar2(100) not null,
      EXTERNAL_RAW_BATCH_ID varchar2(100),
      ARTICUL varchar2(40),
      SUPPLIER_ID varchar2(100),
      PRODUCER_NAME varchar2(255),
      PRODUCED_DATE_FROM date,
      PRODUCED_DATE_TO date,
      EXPIRY_DATE_FROM date,
      EXPIRY_DATE_TO date,
      QUANTITY_INITIAL number,
      QUANTITY_AVAILABLE number,
      UNIT_CODE varchar2(20),
      WARE_ID number,
      QUALITY_STATUS varchar2(30) default 'ACCEPTED',
      MERCURY_STOCK_ENTRY_UUID varchar2(64),
      MERCURY_VSD_UUID varchar2(64),
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(50),
      constraint RRL_RAW_BATCH_PK primary key (RAW_BATCH_ID),
      constraint RRL_RAW_BATCH_U1 unique (RAW_BATCH_NO, ARTICUL, WARE_ID)
    )
  ]');

  ensure_table('RRL_PROD_RAW_USAGE', q'[
    create table RRL_PROD_RAW_USAGE (
      RAW_USAGE_ID number not null,
      PROD_BATCH_ID number,
      PRODUCTION_ORDER_ID number,
      RAW_BATCH_ID number,
      RAW_ARTICUL varchar2(40),
      QUANTITY_PLANNED number,
      QUANTITY_FACT number,
      UNIT_CODE varchar2(20),
      USED_AT date default sysdate,
      USED_BY varchar2(50),
      MERCURY_RAW_LINE_NO number,
      constraint RRL_PROD_RAW_USAGE_PK primary key (RAW_USAGE_ID)
    )
  ]');

  ensure_table('RRL_MERCURY_BATCH', q'[
    create table RRL_MERCURY_BATCH (
      PROD_BATCH_ID number not null,
      MERCURY_OPERATION_ID varchar2(100),
      LOCAL_TRANSACTION_ID varchar2(100),
      STOCK_ENTRY_UUID varchar2(64),
      STOCK_ENTRY_GUID varchar2(64),
      VET_DOCUMENT_UUID varchar2(64),
      VET_DOCUMENT_STATUS varchar2(50),
      VET_DOCUMENT_TYPE varchar2(50),
      VET_DOCUMENT_FORM varchar2(50),
      ISSUE_DATE date,
      FINALIZE_FLAG number(1) default 0,
      PRODUCT_TYPE_GUID varchar2(64),
      PRODUCT_GUID varchar2(64),
      SUBPRODUCT_GUID varchar2(64),
      PRODUCT_ITEM_GUID varchar2(64),
      PRODUCT_ITEM_NAME varchar2(255),
      UNIT_UUID varchar2(64),
      PACKING_FORM_UUID varchar2(64),
      PACKING_AMOUNT number,
      PRODUCER_ENTERPRISE_GUID varchar2(64),
      PRODUCER_ENTERPRISE_UUID varchar2(64),
      OWNER_BUSINESS_GUID varchar2(64),
      OWNER_BUSINESS_UUID varchar2(64),
      LAST_REQUEST_ID number,
      LAST_ERROR varchar2(4000),
      UPDATED_AT date,
      constraint RRL_MERCURY_BATCH_PK primary key (PROD_BATCH_ID)
    )
  ]');

  ensure_table('RRL_CRPT_CODES', q'[
    create table RRL_CRPT_CODES (
      CRPT_CODE_ID number not null,
      PROD_BATCH_ID number,
      UID_PALLET varchar2(50),
      GTIN varchar2(14),
      CIS varchar2(255) not null,
      SERIAL_NO varchar2(100),
      DATAMATRIX_FULL varchar2(4000),
      CODE_STATUS varchar2(30) default 'RESERVED',
      APPLIED_AT date,
      SCANNED_AT date,
      INTRODUCED_AT date,
      PARENT_SSCC varchar2(32),
      CREATED_AT date default sysdate,
      constraint RRL_CRPT_CODES_PK primary key (CRPT_CODE_ID),
      constraint RRL_CRPT_CODES_U1 unique (CIS)
    )
  ]');

  ensure_table('RRL_CRPT_AGGREGATION', q'[
    create table RRL_CRPT_AGGREGATION (
      AGGREGATION_ID number not null,
      SSCC varchar2(32) not null,
      PROD_BATCH_ID number,
      UID_PALLET varchar2(50),
      PARENT_SSCC varchar2(32),
      AGGREGATION_LEVEL varchar2(20),
      AGGREGATION_STATUS varchar2(30) default 'DRAFT',
      CRPT_DOCUMENT_ID varchar2(100),
      SENT_AT date,
      ACCEPTED_AT date,
      ERROR_TEXT varchar2(4000),
      CREATED_AT date default sysdate,
      constraint RRL_CRPT_AGGREGATION_PK primary key (AGGREGATION_ID),
      constraint RRL_CRPT_AGGREGATION_U1 unique (SSCC)
    )
  ]');

  ensure_table('RRL_CRPT_AGGREGATION_ITEMS', q'[
    create table RRL_CRPT_AGGREGATION_ITEMS (
      AGGREGATION_ID number not null,
      CHILD_TYPE varchar2(20) not null,
      CHILD_CIS varchar2(255),
      CHILD_SSCC varchar2(32),
      GTIN varchar2(14),
      PROD_BATCH_ID number,
      CREATED_AT date default sysdate,
      constraint RRL_CRPT_AGG_ITEMS_C1 check (CHILD_TYPE in ('CIS', 'SSCC'))
    )
  ]');

  ensure_table('RRL_REGULATORY_OUTBOX', q'[
    create table RRL_REGULATORY_OUTBOX (
      OUTBOX_ID number not null,
      SYSTEM_CODE varchar2(20) not null,
      EVENT_TYPE varchar2(50) not null,
      PROD_BATCH_ID number,
      UID_PALLET varchar2(50),
      DOCUMENT_NO varchar2(100),
      PAYLOAD_JSON clob,
      STATUS varchar2(30) default 'PENDING' not null,
      TRY_COUNT number default 0 not null,
      LAST_ERROR varchar2(4000),
      CREATED_AT date default sysdate,
      SENT_AT date,
      ACCEPTED_AT date,
      IDEMPOTENCY_KEY varchar2(100),
      constraint RRL_REGULATORY_OUTBOX_PK primary key (OUTBOX_ID)
    )
  ]');

  ensure_table('RRL_FILE_EXCHANGE_LOG', q'[
    create table RRL_FILE_EXCHANGE_LOG (
      FILE_LOG_ID number not null,
      EXCHANGE_TYPE varchar2(50) not null,
      SOURCE_SYSTEM varchar2(100),
      MESSAGE_ID varchar2(100) not null,
      EXTERNAL_OPERATION_ID varchar2(100),
      FILE_NAME varchar2(512),
      FILE_PATH varchar2(1024),
      FILE_HASH varchar2(128),
      STATUS varchar2(30) default 'RECEIVED' not null,
      ERROR_CODE varchar2(100),
      ERROR_TEXT varchar2(4000),
      RECEIVED_AT date default sysdate,
      PROCESSED_AT date,
      PROCESSED_BY varchar2(100),
      CREATED_PROD_BATCH_ID number,
      constraint RRL_FILE_EXCHANGE_LOG_PK primary key (FILE_LOG_ID),
      constraint RRL_FILE_EXCHANGE_LOG_U1 unique (MESSAGE_ID)
    )
  ]');

  ensure_sequence('RRL_PROD_BATCH_SQ', 'create sequence RRL_PROD_BATCH_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_RAW_BATCH_SQ', 'create sequence RRL_RAW_BATCH_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PROD_RAW_USAGE_SQ', 'create sequence RRL_PROD_RAW_USAGE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CRPT_CODES_SQ', 'create sequence RRL_CRPT_CODES_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CRPT_AGGREGATION_SQ', 'create sequence RRL_CRPT_AGGREGATION_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_REGULATORY_OUTBOX_SQ', 'create sequence RRL_REGULATORY_OUTBOX_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_FILE_EXCHANGE_LOG_SQ', 'create sequence RRL_FILE_EXCHANGE_LOG_SQ start with 1 increment by 1 nocache');

  ensure_column('RRL_PALLETS', 'PROD_BATCH_ID', 'PROD_BATCH_ID number');
  ensure_column('RRL_PALLETS', 'SSCC', 'SSCC varchar2(32)');
  ensure_column('RRL_PALLETS', 'MERCURY_STATUS', 'MERCURY_STATUS varchar2(30)');
  ensure_column('RRL_PALLETS', 'CRPT_STATUS', 'CRPT_STATUS varchar2(30)');
  ensure_column('RRL_PALLETS', 'QUALITY_STATUS', 'QUALITY_STATUS varchar2(30)');

  ensure_column('RRL_SBORKA_PALLET_ROWS', 'PROD_BATCH_ID', 'PROD_BATCH_ID number');
  ensure_column('RRL_SBORKA_PALLET_ROWS', 'SSCC', 'SSCC varchar2(32)');
  ensure_column('RRL_SBORKA_PALLET_ROWS', 'CRPT_TRANSFER_MODE', 'CRPT_TRANSFER_MODE varchar2(20)');

  ensure_index('RRL_PROD_BATCH_I1', 'create index RRL_PROD_BATCH_I1 on RRL_PROD_BATCH (ARTICUL, GTIN, WARE_ID)');
  ensure_index('RRL_PROD_BATCH_I2', 'create index RRL_PROD_BATCH_I2 on RRL_PROD_BATCH (SOURCE_SYSTEM, SOURCE_MESSAGE_ID)');
  ensure_index('RRL_PROD_BATCH_PALLETS_I1', 'create index RRL_PROD_BATCH_PALLETS_I1 on RRL_PROD_BATCH_PALLETS (UID_PALLET)');
  ensure_index('RRL_RAW_BATCH_I1', 'create index RRL_RAW_BATCH_I1 on RRL_RAW_BATCH (ARTICUL, WARE_ID)');
  ensure_index('RRL_PROD_RAW_USAGE_I1', 'create index RRL_PROD_RAW_USAGE_I1 on RRL_PROD_RAW_USAGE (PROD_BATCH_ID)');
  ensure_index('RRL_PROD_RAW_USAGE_I2', 'create index RRL_PROD_RAW_USAGE_I2 on RRL_PROD_RAW_USAGE (RAW_BATCH_ID)');
  ensure_index('RRL_CRPT_CODES_I1', 'create index RRL_CRPT_CODES_I1 on RRL_CRPT_CODES (PROD_BATCH_ID, UID_PALLET)');
  ensure_index('RRL_CRPT_CODES_I2', 'create index RRL_CRPT_CODES_I2 on RRL_CRPT_CODES (PARENT_SSCC)');
  ensure_index('RRL_CRPT_AGG_ITEMS_I1', 'create index RRL_CRPT_AGG_ITEMS_I1 on RRL_CRPT_AGGREGATION_ITEMS (AGGREGATION_ID)');
  ensure_index('RRL_REGULATORY_OUTBOX_I1', 'create index RRL_REGULATORY_OUTBOX_I1 on RRL_REGULATORY_OUTBOX (STATUS, SYSTEM_CODE, CREATED_AT)');
  ensure_index('RRL_FILE_EXCHANGE_LOG_I1', 'create index RRL_FILE_EXCHANGE_LOG_I1 on RRL_FILE_EXCHANGE_LOG (STATUS, RECEIVED_AT)');
  ensure_index('RRL_PALLETS_I_PROD_BATCH', 'create index RRL_PALLETS_I_PROD_BATCH on RRL_PALLETS (PROD_BATCH_ID)');
  ensure_index('RRL_PALLETS_I_SSCC', 'create index RRL_PALLETS_I_SSCC on RRL_PALLETS (SSCC)');
  ensure_index('RRL_SB_PAL_ROWS_I_PROD_BATCH', 'create index RRL_SB_PAL_ROWS_I_PROD_BATCH on RRL_SBORKA_PALLET_ROWS (PROD_BATCH_ID)');
end;
/

merge into RRL_SYSTEM_SETTINGS d
using (
  select 'PRODUCTION_BATCH_SOURCE' setting_key, 'MANUAL' setting_value,
         'MANUAL, FILE_EXCHANGE, or API source for production batch release' description
    from dual
  union all
  select 'PROD_EXCHANGE_ROOT_DIR', null,
         'Root directory for production_release folder exchange'
    from dual
  union all
  select 'PROD_EXCHANGE_ENABLED', '0',
         '1 enables production release JSON file exchange worker'
    from dual
) s
on (d.SETTING_KEY = s.SETTING_KEY)
when not matched then
  insert (SETTING_KEY, SETTING_VALUE, DESCRIPTION, UPDATED_AT, UPDATED_BY)
  values (s.SETTING_KEY, s.SETTING_VALUE, s.DESCRIPTION, sysdate, user);

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-001-feed-factory-traceability' migration_id,
         'Feed factory traceability base schema' description,
         '001_apply.sql' script_name,
         '001_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-001] Apply finished. Run 001_verify.sql.
