prompt [migration 2026-05-17-003] Regulatory lifecycle entities - apply

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
  ensure_table('RRL_MERCURY_SITE', q'[
    create table RRL_MERCURY_SITE (
      MERCURY_SITE_ID number not null,
      SITE_CODE varchar2(100) not null,
      SITE_NAME varchar2(255),
      WARE_ID number,
      ENTERPRISE_GUID varchar2(64),
      ENTERPRISE_UUID varchar2(64),
      BUSINESS_GUID varchar2(64),
      BUSINESS_UUID varchar2(64),
      ADDRESS_TEXT varchar2(1000),
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(100),
      UPDATED_AT date,
      UPDATED_BY varchar2(100),
      constraint RRL_MERCURY_SITE_PK primary key (MERCURY_SITE_ID),
      constraint RRL_MERCURY_SITE_U1 unique (SITE_CODE)
    )
  ]');

  ensure_table('RRL_MERCURY_OPERATION', q'[
    create table RRL_MERCURY_OPERATION (
      MERCURY_OPERATION_ROW_ID number not null,
      PROD_BATCH_ID number,
      RAW_BATCH_ID number,
      MERCURY_SITE_ID number,
      OPERATION_TYPE varchar2(50) not null,
      MERCURY_OPERATION_ID varchar2(100),
      EXTERNAL_OPERATION_ID varchar2(100),
      STATUS varchar2(30) default 'DRAFT' not null,
      REQUEST_JSON clob,
      RESPONSE_JSON clob,
      LAST_ERROR varchar2(4000),
      STARTED_AT date,
      FINISHED_AT date,
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(100),
      UPDATED_AT date,
      UPDATED_BY varchar2(100),
      constraint RRL_MERCURY_OPERATION_PK primary key (MERCURY_OPERATION_ROW_ID)
    )
  ]');

  ensure_table('RRL_REG_OPERATION_JOURNAL', q'[
    create table RRL_REG_OPERATION_JOURNAL (
      JOURNAL_ID number not null,
      SYSTEM_CODE varchar2(20) not null,
      ENTITY_TYPE varchar2(50) not null,
      ENTITY_ID varchar2(255),
      PROD_BATCH_ID number,
      RAW_BATCH_ID number,
      UID_PALLET varchar2(50),
      SSCC varchar2(32),
      OPERATION_TYPE varchar2(50) not null,
      OLD_STATUS varchar2(50),
      NEW_STATUS varchar2(50),
      DOCUMENT_ID varchar2(100),
      EXTERNAL_OPERATION_ID varchar2(100),
      PAYLOAD_JSON clob,
      MESSAGE varchar2(4000),
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(100),
      constraint RRL_REG_OPERATION_JOURNAL_PK primary key (JOURNAL_ID)
    )
  ]');

  ensure_table('RRL_CRPT_CIRCULATION', q'[
    create table RRL_CRPT_CIRCULATION (
      CIRCULATION_ID number not null,
      EVENT_TYPE varchar2(30) not null,
      PROD_BATCH_ID number,
      UID_PALLET varchar2(50),
      SSCC varchar2(32),
      CIS varchar2(255),
      DOCUMENT_ID varchar2(100),
      DOCUMENT_NO varchar2(100),
      STATUS varchar2(30) default 'PENDING' not null,
      PAYLOAD_JSON clob,
      SENT_AT date,
      ACCEPTED_AT date,
      ERROR_TEXT varchar2(4000),
      CREATED_AT date default sysdate,
      CREATED_BY varchar2(100),
      constraint RRL_CRPT_CIRCULATION_PK primary key (CIRCULATION_ID),
      constraint RRL_CRPT_CIRCULATION_C1 check (EVENT_TYPE in ('INTRODUCE', 'WITHDRAW'))
    )
  ]');

  ensure_sequence('RRL_MERCURY_SITE_SQ', 'create sequence RRL_MERCURY_SITE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MERCURY_OPERATION_SQ', 'create sequence RRL_MERCURY_OPERATION_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_REG_OPERATION_JOURNAL_SQ', 'create sequence RRL_REG_OPERATION_JOURNAL_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CRPT_CIRCULATION_SQ', 'create sequence RRL_CRPT_CIRCULATION_SQ start with 1 increment by 1 nocache');

  ensure_column('RRL_PROD_BATCH', 'MERCURY_SITE_ID', 'MERCURY_SITE_ID number');
  ensure_column('RRL_RAW_BATCH', 'MERCURY_SITE_ID', 'MERCURY_SITE_ID number');
  ensure_column('RRL_MERCURY_BATCH', 'MERCURY_SITE_ID', 'MERCURY_SITE_ID number');
  ensure_column('RRL_CRPT_CODES', 'WITHDRAWN_AT', 'WITHDRAWN_AT date');
  ensure_column('RRL_CRPT_CODES', 'INTRODUCTION_DOCUMENT_ID', 'INTRODUCTION_DOCUMENT_ID varchar2(100)');
  ensure_column('RRL_CRPT_CODES', 'WITHDRAWAL_DOCUMENT_ID', 'WITHDRAWAL_DOCUMENT_ID varchar2(100)');
  ensure_column('RRL_CRPT_CODES', 'LAST_STATUS_AT', 'LAST_STATUS_AT date');
  ensure_column('RRL_CRPT_CODES', 'LAST_ERROR', 'LAST_ERROR varchar2(4000)');

  ensure_index('RRL_MERCURY_SITE_I1', 'create index RRL_MERCURY_SITE_I1 on RRL_MERCURY_SITE (WARE_ID)');
  ensure_index('RRL_MERCURY_OPERATION_I1', 'create index RRL_MERCURY_OPERATION_I1 on RRL_MERCURY_OPERATION (PROD_BATCH_ID, OPERATION_TYPE)');
  ensure_index('RRL_MERCURY_OPERATION_I2', 'create index RRL_MERCURY_OPERATION_I2 on RRL_MERCURY_OPERATION (STATUS, CREATED_AT)');
  ensure_index('RRL_REG_OPERATION_JOURNAL_I1', 'create index RRL_REG_OPERATION_JOURNAL_I1 on RRL_REG_OPERATION_JOURNAL (SYSTEM_CODE, CREATED_AT)');
  ensure_index('RRL_REG_OPERATION_JOURNAL_I2', 'create index RRL_REG_OPERATION_JOURNAL_I2 on RRL_REG_OPERATION_JOURNAL (PROD_BATCH_ID, CREATED_AT)');
  ensure_index('RRL_CRPT_CIRCULATION_I1', 'create index RRL_CRPT_CIRCULATION_I1 on RRL_CRPT_CIRCULATION (EVENT_TYPE, STATUS, CREATED_AT)');
  ensure_index('RRL_CRPT_CIRCULATION_I2', 'create index RRL_CRPT_CIRCULATION_I2 on RRL_CRPT_CIRCULATION (CIS)');
end;
/

create or replace package RRL_REGULATORY_API as
  function upsert_mercury_site(
    p_site_code           varchar2,
    p_site_name           varchar2 default null,
    p_ware_id             number default null,
    p_enterprise_guid     varchar2 default null,
    p_enterprise_uuid     varchar2 default null,
    p_business_guid       varchar2 default null,
    p_business_uuid       varchar2 default null,
    p_address_text        varchar2 default null,
    p_active              number default 1,
    p_updated_by          varchar2 default user
  ) return number;

  function create_mercury_operation(
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_mercury_site_id     number default null,
    p_operation_type      varchar2,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_status              varchar2 default 'DRAFT',
    p_request_json        clob default null,
    p_created_by          varchar2 default user
  ) return number;

  procedure update_mercury_operation(
    p_operation_row_id    number,
    p_status              varchar2 default null,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_response_json       clob default null,
    p_last_error          varchar2 default null,
    p_updated_by          varchar2 default user
  );

  function write_journal(
    p_system_code         varchar2,
    p_entity_type         varchar2,
    p_entity_id           varchar2 default null,
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_uid_pallet          varchar2 default null,
    p_sscc                varchar2 default null,
    p_operation_type      varchar2,
    p_old_status          varchar2 default null,
    p_new_status          varchar2 default null,
    p_document_id         varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_payload_json        clob default null,
    p_message             varchar2 default null,
    p_created_by          varchar2 default user
  ) return number;

  function set_crpt_code_status(
    p_cis                 varchar2,
    p_code_status         varchar2,
    p_event_type          varchar2 default null,
    p_document_id         varchar2 default null,
    p_document_no         varchar2 default null,
    p_payload_json        clob default null,
    p_error_text          varchar2 default null,
    p_updated_by          varchar2 default user
  ) return number;
end RRL_REGULATORY_API;
/

create or replace package body RRL_REGULATORY_API as
  function upsert_mercury_site(
    p_site_code           varchar2,
    p_site_name           varchar2 default null,
    p_ware_id             number default null,
    p_enterprise_guid     varchar2 default null,
    p_enterprise_uuid     varchar2 default null,
    p_business_guid       varchar2 default null,
    p_business_uuid       varchar2 default null,
    p_address_text        varchar2 default null,
    p_active              number default 1,
    p_updated_by          varchar2 default user
  ) return number is
    v_id number;
  begin
    begin
      select MERCURY_SITE_ID into v_id
        from RRL_MERCURY_SITE
       where SITE_CODE = p_site_code;
    exception
      when no_data_found then
        select RRL_MERCURY_SITE_SQ.nextval into v_id from dual;
        insert into RRL_MERCURY_SITE (
          MERCURY_SITE_ID, SITE_CODE, SITE_NAME, WARE_ID,
          ENTERPRISE_GUID, ENTERPRISE_UUID, BUSINESS_GUID, BUSINESS_UUID,
          ADDRESS_TEXT, ACTIVE, CREATED_AT, CREATED_BY
        ) values (
          v_id, p_site_code, p_site_name, p_ware_id,
          p_enterprise_guid, p_enterprise_uuid, p_business_guid, p_business_uuid,
          p_address_text, nvl(p_active, 1), sysdate, p_updated_by
        );
        return v_id;
    end;

    update RRL_MERCURY_SITE
       set SITE_NAME = nvl(p_site_name, SITE_NAME),
           WARE_ID = nvl(p_ware_id, WARE_ID),
           ENTERPRISE_GUID = nvl(p_enterprise_guid, ENTERPRISE_GUID),
           ENTERPRISE_UUID = nvl(p_enterprise_uuid, ENTERPRISE_UUID),
           BUSINESS_GUID = nvl(p_business_guid, BUSINESS_GUID),
           BUSINESS_UUID = nvl(p_business_uuid, BUSINESS_UUID),
           ADDRESS_TEXT = nvl(p_address_text, ADDRESS_TEXT),
           ACTIVE = nvl(p_active, ACTIVE),
           UPDATED_AT = sysdate,
           UPDATED_BY = p_updated_by
     where MERCURY_SITE_ID = v_id;

    return v_id;
  end upsert_mercury_site;

  function create_mercury_operation(
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_mercury_site_id     number default null,
    p_operation_type      varchar2,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_status              varchar2 default 'DRAFT',
    p_request_json        clob default null,
    p_created_by          varchar2 default user
  ) return number is
    v_id number;
    v_journal_id number;
  begin
    if p_mercury_operation_id is not null then
      begin
        select MERCURY_OPERATION_ROW_ID into v_id
          from RRL_MERCURY_OPERATION
         where MERCURY_OPERATION_ID = p_mercury_operation_id
           and rownum = 1;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    select RRL_MERCURY_OPERATION_SQ.nextval into v_id from dual;

    insert into RRL_MERCURY_OPERATION (
      MERCURY_OPERATION_ROW_ID, PROD_BATCH_ID, RAW_BATCH_ID, MERCURY_SITE_ID,
      OPERATION_TYPE, MERCURY_OPERATION_ID, EXTERNAL_OPERATION_ID, STATUS,
      REQUEST_JSON, STARTED_AT, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_prod_batch_id, p_raw_batch_id, p_mercury_site_id,
      p_operation_type, p_mercury_operation_id, p_external_operation_id, nvl(p_status, 'DRAFT'),
      p_request_json, case when nvl(p_status, 'DRAFT') in ('SENT', 'PROCESSING') then sysdate else null end,
      sysdate, p_created_by
    );

    v_journal_id := write_journal(
      p_system_code => 'MERCURY',
      p_entity_type => 'MERCURY_OPERATION',
      p_entity_id => to_char(v_id),
      p_prod_batch_id => p_prod_batch_id,
      p_raw_batch_id => p_raw_batch_id,
      p_operation_type => p_operation_type,
      p_new_status => nvl(p_status, 'DRAFT'),
      p_external_operation_id => p_external_operation_id,
      p_payload_json => p_request_json,
      p_created_by => p_created_by
    );

    if p_prod_batch_id is not null and p_mercury_site_id is not null then
      update RRL_PROD_BATCH
         set MERCURY_SITE_ID = p_mercury_site_id,
             UPDATED_AT = sysdate,
             UPDATED_BY = p_created_by
       where PROD_BATCH_ID = p_prod_batch_id;
    end if;

    return v_id;
  end create_mercury_operation;

  procedure update_mercury_operation(
    p_operation_row_id    number,
    p_status              varchar2 default null,
    p_mercury_operation_id varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_response_json       clob default null,
    p_last_error          varchar2 default null,
    p_updated_by          varchar2 default user
  ) is
    v_old_status varchar2(50);
    v_new_status varchar2(50);
    v_prod_batch_id number;
    v_raw_batch_id number;
    v_journal_id number;
  begin
    select STATUS, PROD_BATCH_ID, RAW_BATCH_ID
      into v_old_status, v_prod_batch_id, v_raw_batch_id
      from RRL_MERCURY_OPERATION
     where MERCURY_OPERATION_ROW_ID = p_operation_row_id;

    v_new_status := nvl(p_status, v_old_status);

    update RRL_MERCURY_OPERATION
       set STATUS = v_new_status,
           MERCURY_OPERATION_ID = nvl(p_mercury_operation_id, MERCURY_OPERATION_ID),
           EXTERNAL_OPERATION_ID = nvl(p_external_operation_id, EXTERNAL_OPERATION_ID),
           RESPONSE_JSON = nvl(p_response_json, RESPONSE_JSON),
           LAST_ERROR = substr(p_last_error, 1, 4000),
           FINISHED_AT = case when v_new_status in ('ACCEPTED', 'REJECTED', 'ERROR', 'DONE') then sysdate else FINISHED_AT end,
           UPDATED_AT = sysdate,
           UPDATED_BY = p_updated_by
     where MERCURY_OPERATION_ROW_ID = p_operation_row_id;

    v_journal_id := write_journal(
      p_system_code => 'MERCURY',
      p_entity_type => 'MERCURY_OPERATION',
      p_entity_id => to_char(p_operation_row_id),
      p_prod_batch_id => v_prod_batch_id,
      p_raw_batch_id => v_raw_batch_id,
      p_operation_type => 'STATUS',
      p_old_status => v_old_status,
      p_new_status => v_new_status,
      p_external_operation_id => p_external_operation_id,
      p_payload_json => p_response_json,
      p_message => p_last_error,
      p_created_by => p_updated_by
    );
  end update_mercury_operation;

  function write_journal(
    p_system_code         varchar2,
    p_entity_type         varchar2,
    p_entity_id           varchar2 default null,
    p_prod_batch_id       number default null,
    p_raw_batch_id        number default null,
    p_uid_pallet          varchar2 default null,
    p_sscc                varchar2 default null,
    p_operation_type      varchar2,
    p_old_status          varchar2 default null,
    p_new_status          varchar2 default null,
    p_document_id         varchar2 default null,
    p_external_operation_id varchar2 default null,
    p_payload_json        clob default null,
    p_message             varchar2 default null,
    p_created_by          varchar2 default user
  ) return number is
    v_id number;
  begin
    select RRL_REG_OPERATION_JOURNAL_SQ.nextval into v_id from dual;

    insert into RRL_REG_OPERATION_JOURNAL (
      JOURNAL_ID, SYSTEM_CODE, ENTITY_TYPE, ENTITY_ID, PROD_BATCH_ID, RAW_BATCH_ID,
      UID_PALLET, SSCC, OPERATION_TYPE, OLD_STATUS, NEW_STATUS, DOCUMENT_ID,
      EXTERNAL_OPERATION_ID, PAYLOAD_JSON, MESSAGE, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_system_code, p_entity_type, p_entity_id, p_prod_batch_id, p_raw_batch_id,
      p_uid_pallet, p_sscc, p_operation_type, p_old_status, p_new_status, p_document_id,
      p_external_operation_id, p_payload_json, substr(p_message, 1, 4000), sysdate, p_created_by
    );

    return v_id;
  end write_journal;

  function set_crpt_code_status(
    p_cis                 varchar2,
    p_code_status         varchar2,
    p_event_type          varchar2 default null,
    p_document_id         varchar2 default null,
    p_document_no         varchar2 default null,
    p_payload_json        clob default null,
    p_error_text          varchar2 default null,
    p_updated_by          varchar2 default user
  ) return number is
    v_code_id number;
    v_prod_batch_id number;
    v_uid_pallet varchar2(50);
    v_parent_sscc varchar2(32);
    v_old_status varchar2(50);
    v_circ_id number;
    v_event_type varchar2(30);
    v_journal_id number;
  begin
    select CRPT_CODE_ID, PROD_BATCH_ID, UID_PALLET, PARENT_SSCC, CODE_STATUS
      into v_code_id, v_prod_batch_id, v_uid_pallet, v_parent_sscc, v_old_status
      from RRL_CRPT_CODES
     where CIS = p_cis;

    v_event_type := upper(p_event_type);

    update RRL_CRPT_CODES
       set CODE_STATUS = p_code_status,
           INTRODUCED_AT = case when v_event_type = 'INTRODUCE' then sysdate else INTRODUCED_AT end,
           WITHDRAWN_AT = case when v_event_type = 'WITHDRAW' then sysdate else WITHDRAWN_AT end,
           INTRODUCTION_DOCUMENT_ID = case when v_event_type = 'INTRODUCE' then p_document_id else INTRODUCTION_DOCUMENT_ID end,
           WITHDRAWAL_DOCUMENT_ID = case when v_event_type = 'WITHDRAW' then p_document_id else WITHDRAWAL_DOCUMENT_ID end,
           LAST_STATUS_AT = sysdate,
           LAST_ERROR = substr(p_error_text, 1, 4000)
     where CRPT_CODE_ID = v_code_id;

    if v_event_type in ('INTRODUCE', 'WITHDRAW') then
      select RRL_CRPT_CIRCULATION_SQ.nextval into v_circ_id from dual;

      insert into RRL_CRPT_CIRCULATION (
        CIRCULATION_ID, EVENT_TYPE, PROD_BATCH_ID, UID_PALLET, SSCC, CIS,
        DOCUMENT_ID, DOCUMENT_NO, STATUS, PAYLOAD_JSON, ACCEPTED_AT,
        ERROR_TEXT, CREATED_AT, CREATED_BY
      ) values (
        v_circ_id, v_event_type, v_prod_batch_id, v_uid_pallet, v_parent_sscc, p_cis,
        p_document_id, p_document_no, p_code_status, p_payload_json,
        case when p_error_text is null then sysdate else null end,
        substr(p_error_text, 1, 4000), sysdate, p_updated_by
      );
    end if;

    v_journal_id := write_journal(
      p_system_code => 'CRPT',
      p_entity_type => 'CRPT_CODE',
      p_entity_id => p_cis,
      p_prod_batch_id => v_prod_batch_id,
      p_uid_pallet => v_uid_pallet,
      p_sscc => v_parent_sscc,
      p_operation_type => nvl(v_event_type, 'STATUS'),
      p_old_status => v_old_status,
      p_new_status => p_code_status,
      p_document_id => p_document_id,
      p_payload_json => p_payload_json,
      p_message => p_error_text,
      p_created_by => p_updated_by
    );

    return v_code_id;
  end set_crpt_code_status;
end RRL_REGULATORY_API;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-003-regulatory-lifecycle-entities' migration_id,
         'Mercury sites, regulatory operation journal, CRPT lifecycle tables and API package' description,
         '003_apply.sql' script_name,
         '003_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-003] Apply finished. Run 003_verify.sql.
