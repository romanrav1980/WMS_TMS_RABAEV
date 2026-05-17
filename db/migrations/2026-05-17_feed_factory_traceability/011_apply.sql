prompt [migration 2026-05-17-011] MES production completion - apply

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

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      begin
        execute immediate p_sql;
      exception
        when others then
          if sqlcode = -1408 then
            null;
          else
            raise;
          end if;
      end;
    end if;
  end;

  procedure ensure_varchar_length(p_table varchar2, p_column varchar2, p_length number) is
    n number;
    l number;
  begin
    select count(*)
      into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column)
       and data_type = 'VARCHAR2';

    if n > 0 then
      select char_length
        into l
        from user_tab_columns
       where table_name = upper(p_table)
         and column_name = upper(p_column)
         and data_type = 'VARCHAR2';

      if l < p_length then
        execute immediate 'alter table ' || p_table || ' modify (' || p_column || ' varchar2(' || p_length || '))';
      end if;
    end if;
  end;
begin
  ensure_varchar_length('RRL_PROD_BATCH_PALLETS', 'UID_PALLET', 200);
  ensure_varchar_length('RRL_CRPT_CODES', 'UID_PALLET', 200);
  ensure_varchar_length('RRL_CRPT_AGGREGATION', 'UID_PALLET', 200);
  ensure_varchar_length('RRL_EVENTS', 'UID_POLETA', 200);
  ensure_varchar_length('RRL_REMAINS', 'UID_POLETA', 200);

  ensure_table('RRL_PRODUCTION_ORDER', q'[
    create table RRL_PRODUCTION_ORDER (
      PRODUCTION_ORDER_ID number not null,
      ORDER_NO varchar2(100) not null,
      BOM_ID number not null,
      TARGET_ARTICUL varchar2(40) not null,
      TARGET_MOD_ID number,
      TARGET_GTIN varchar2(14),
      PLANNED_QTY number not null,
      FACT_QTY number,
      UNIT_CODE varchar2(20) default 'KG' not null,
      WARE_ID number,
      PRODUCTION_LINE varchar2(100),
      SHIFT_ID varchar2(50),
      STATUS varchar2(30) default 'DRAFT' not null,
      PLANNED_START_AT date,
      PLANNED_FINISH_AT date,
      STARTED_AT date,
      COMPLETED_AT date,
      PROD_BATCH_ID number,
      IDEMPOTENCY_KEY varchar2(100),
      SOURCE_SYSTEM varchar2(50),
      SOURCE_MESSAGE_ID varchar2(100),
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_PRODUCTION_ORDER_PK primary key (PRODUCTION_ORDER_ID),
      constraint RRL_PRODUCTION_ORDER_U1 unique (ORDER_NO),
      constraint RRL_PRODUCTION_ORDER_U2 unique (IDEMPOTENCY_KEY),
      constraint RRL_PRODUCTION_ORDER_FK1 foreign key (BOM_ID) references RRL_BOM (BOM_ID),
      constraint RRL_PRODUCTION_ORDER_CHK1 check (PLANNED_QTY > 0),
      constraint RRL_PRODUCTION_ORDER_CHK2 check (FACT_QTY is null or FACT_QTY >= 0),
      constraint RRL_PRODUCTION_ORDER_CHK3 check (STATUS in ('DRAFT', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
    )
  ]');

  ensure_table('RRL_PROD_ORDER_BOM_LINE', q'[
    create table RRL_PROD_ORDER_BOM_LINE (
      ORDER_LINE_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      BOM_ID number not null,
      BOM_LINE_ID number,
      LINE_NO number not null,
      COMPONENT_TYPE varchar2(30) not null,
      COMPONENT_ARTICUL varchar2(40),
      COMPONENT_MOD_ID number,
      COMPONENT_NAME varchar2(255),
      PLANNED_QTY number,
      UNIT_CODE varchar2(20),
      LOSS_PERCENT number default 0 not null,
      IS_REQUIRED number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_PROD_ORDER_BOM_LINE_PK primary key (ORDER_LINE_ID),
      constraint RRL_PROD_ORDER_BOM_LINE_U1 unique (PRODUCTION_ORDER_ID, LINE_NO),
      constraint RRL_PROD_ORDER_BOM_LINE_FK1 foreign key (PRODUCTION_ORDER_ID) references RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID),
      constraint RRL_PROD_ORDER_BOM_LINE_FK2 foreign key (BOM_ID) references RRL_BOM (BOM_ID),
      constraint RRL_PROD_ORDER_BOM_LINE_CHK1 check (PLANNED_QTY is null or PLANNED_QTY >= 0)
    )
  ]');

  ensure_table('RRL_MES_MOVEMENT', q'[
    create table RRL_MES_MOVEMENT (
      MOVEMENT_ID number not null,
      MOVEMENT_TYPE varchar2(40) not null,
      PRODUCTION_ORDER_ID number,
      PROD_BATCH_ID number,
      BOM_ID number,
      BOM_LINE_ID number,
      RAW_BATCH_ID number,
      RAW_ARTICUL varchar2(40),
      UID_PALLET varchar2(200),
      SSCC varchar2(50),
      QUANTITY number,
      PACK_COUNT number,
      UNIT_CODE varchar2(20),
      SOURCE_LOCATION varchar2(100),
      TARGET_LOCATION varchar2(100),
      STATUS varchar2(30) default 'MES_POSTED' not null,
      PAYLOAD_JSON clob,
      WMS_APPLIED_AT date,
      WMS_APPLIED_BY varchar2(50),
      RETRY_COUNT number default 0 not null,
      LAST_ERROR varchar2(4000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_MES_MOVEMENT_PK primary key (MOVEMENT_ID),
      constraint RRL_MES_MOVEMENT_FK1 foreign key (PRODUCTION_ORDER_ID) references RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID),
      constraint RRL_MES_MOVEMENT_FK2 foreign key (BOM_ID) references RRL_BOM (BOM_ID),
      constraint RRL_MES_MOVEMENT_CHK1 check (MOVEMENT_TYPE in ('RAW_ISSUE_TO_PRODUCTION', 'RAW_CONSUMPTION', 'FG_LOT_RELEASE', 'FG_PALLET_RELEASE')),
      constraint RRL_MES_MOVEMENT_CHK2 check (STATUS in ('MES_POSTED', 'PENDING_WMS_APPLY', 'APPLIED_TO_WMS', 'ERROR', 'CANCELLED')),
      constraint RRL_MES_MOVEMENT_CHK3 check (QUANTITY is null or QUANTITY >= 0),
      constraint RRL_MES_MOVEMENT_CHK4 check (PACK_COUNT is null or PACK_COUNT >= 0)
    )
  ]');

  ensure_table('RRL_MES_COMPLETION', q'[
    create table RRL_MES_COMPLETION (
      COMPLETION_ID number not null,
      PRODUCTION_ORDER_ID number not null,
      PROD_BATCH_ID number not null,
      IDEMPOTENCY_KEY varchar2(100),
      STATUS varchar2(30) default 'DONE' not null,
      PAYLOAD_JSON clob,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_MES_COMPLETION_PK primary key (COMPLETION_ID),
      constraint RRL_MES_COMPLETION_U1 unique (IDEMPOTENCY_KEY),
      constraint RRL_MES_COMPLETION_FK1 foreign key (PRODUCTION_ORDER_ID) references RRL_PRODUCTION_ORDER (PRODUCTION_ORDER_ID)
    )
  ]');

  ensure_sequence('RRL_PRODUCTION_ORDER_SQ', 'create sequence RRL_PRODUCTION_ORDER_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_PROD_ORDER_BOM_LINE_SQ', 'create sequence RRL_PROD_ORDER_BOM_LINE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MES_MOVEMENT_SQ', 'create sequence RRL_MES_MOVEMENT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_MES_COMPLETION_SQ', 'create sequence RRL_MES_COMPLETION_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_PRODUCTION_ORDER_I1', 'create index RRL_PRODUCTION_ORDER_I1 on RRL_PRODUCTION_ORDER (BOM_ID, STATUS, PLANNED_START_AT)');
  ensure_index('RRL_PRODUCTION_ORDER_I2', 'create index RRL_PRODUCTION_ORDER_I2 on RRL_PRODUCTION_ORDER (TARGET_ARTICUL, STATUS)');
  ensure_index('RRL_PROD_ORDER_BOM_LINE_I1', 'create index RRL_PROD_ORDER_BOM_LINE_I1 on RRL_PROD_ORDER_BOM_LINE (PRODUCTION_ORDER_ID, COMPONENT_ARTICUL)');
  ensure_index('RRL_MES_MOVEMENT_I1', 'create index RRL_MES_MOVEMENT_I1 on RRL_MES_MOVEMENT (PRODUCTION_ORDER_ID, MOVEMENT_TYPE, MOVEMENT_ID)');
  ensure_index('RRL_MES_MOVEMENT_I2', 'create index RRL_MES_MOVEMENT_I2 on RRL_MES_MOVEMENT (STATUS, MOVEMENT_ID)');
  ensure_index('RRL_MES_MOVEMENT_I3', 'create index RRL_MES_MOVEMENT_I3 on RRL_MES_MOVEMENT (PROD_BATCH_ID, MOVEMENT_TYPE)');
  ensure_index('RRL_MES_MOVEMENT_I4', 'create index RRL_MES_MOVEMENT_I4 on RRL_MES_MOVEMENT (UID_PALLET)');
end;
/

create or replace package RRL_MES_PRODUCTION_API as
  function create_order(
    p_order_no           varchar2,
    p_bom_id             number default null,
    p_target_articul     varchar2,
    p_planned_qty        number,
    p_unit_code          varchar2 default 'KG',
    p_ware_id            number default null,
    p_production_line    varchar2 default null,
    p_shift_id           varchar2 default null,
    p_planned_start_at   date default null,
    p_planned_finish_at  date default null,
    p_source_system      varchar2 default null,
    p_source_message_id  varchar2 default null,
    p_idempotency_key    varchar2 default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number;

  function issue_raw_to_production(
    p_production_order_id number,
    p_uid_pallet          varchar2 default null,
    p_raw_batch_id        number default null,
    p_raw_articul         varchar2 default null,
    p_quantity            number,
    p_unit_code           varchar2 default 'KG',
    p_source_location     varchar2 default null,
    p_production_location varchar2 default 'MES_PRODUCTION',
    p_created_by          varchar2 default null
  ) return number;

  function complete_order(
    p_production_order_id number,
    p_prod_batch_no       varchar2 default null,
    p_fact_qty            number,
    p_unit_code           varchar2 default 'KG',
    p_pallets_json        clob default null,
    p_idempotency_key     varchar2 default null,
    p_created_by          varchar2 default null
  ) return number;

  procedure apply_mes_movements_to_wms(
    p_production_order_id number,
    p_applied_by          varchar2 default null
  );

  procedure retry_mes_movement(
    p_movement_id number,
    p_updated_by  varchar2 default null
  );
end RRL_MES_PRODUCTION_API;
/

create or replace package body RRL_MES_PRODUCTION_API as
  function next_line_no(p_production_order_id number) return number is
    v_line_no number;
  begin
    select nvl(max(LINE_NO), 0) + 10
      into v_line_no
      from RRL_PROD_ORDER_BOM_LINE
     where PRODUCTION_ORDER_ID = p_production_order_id;
    return v_line_no;
  end;

  function create_order(
    p_order_no           varchar2,
    p_bom_id             number default null,
    p_target_articul     varchar2,
    p_planned_qty        number,
    p_unit_code          varchar2 default 'KG',
    p_ware_id            number default null,
    p_production_line    varchar2 default null,
    p_shift_id           varchar2 default null,
    p_planned_start_at   date default null,
    p_planned_finish_at  date default null,
    p_source_system      varchar2 default null,
    p_source_message_id  varchar2 default null,
    p_idempotency_key    varchar2 default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number is
    v_id number;
    v_bom_id number;
    v_bom RRL_BOM%rowtype;
    v_factor number;
  begin
    if p_idempotency_key is not null then
      begin
        select PRODUCTION_ORDER_ID into v_id
          from RRL_PRODUCTION_ORDER
         where IDEMPOTENCY_KEY = p_idempotency_key;
        return v_id;
      exception
        when no_data_found then null;
      end;
    end if;

    begin
      select PRODUCTION_ORDER_ID into v_id
        from RRL_PRODUCTION_ORDER
       where ORDER_NO = p_order_no;
      return v_id;
    exception
      when no_data_found then null;
    end;

    if p_planned_qty is null or p_planned_qty <= 0 then
      raise_application_error(-20900, 'planned quantity must be greater than zero');
    end if;

    v_bom_id := p_bom_id;
    if v_bom_id is null then
      v_bom_id := RRL_BOM_API.find_primary_bom(
        p_target_articul => p_target_articul,
        p_planned_date => nvl(p_planned_start_at, trunc(sysdate)),
        p_ware_id => p_ware_id,
        p_production_line => p_production_line
      );
    end if;

    if v_bom_id is null then
      raise_application_error(-20901, 'approved primary BOM not found');
    end if;

    select * into v_bom
      from RRL_BOM
     where BOM_ID = v_bom_id
       and STATUS in ('APPROVED', 'ACTIVE');

    if upper(v_bom.TARGET_ARTICUL) <> upper(substr(p_target_articul, 1, 40)) then
      raise_application_error(-20902, 'BOM target articul does not match production order target');
    end if;

    select RRL_PRODUCTION_ORDER_SQ.nextval into v_id from dual;

    insert into RRL_PRODUCTION_ORDER (
      PRODUCTION_ORDER_ID, ORDER_NO, BOM_ID, TARGET_ARTICUL, TARGET_MOD_ID,
      TARGET_GTIN, PLANNED_QTY, UNIT_CODE, WARE_ID, PRODUCTION_LINE, SHIFT_ID,
      STATUS, PLANNED_START_AT, PLANNED_FINISH_AT, IDEMPOTENCY_KEY,
      SOURCE_SYSTEM, SOURCE_MESSAGE_ID, COMMENT_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(p_order_no, 1, 100), v_bom_id, upper(substr(p_target_articul, 1, 40)),
      v_bom.TARGET_MOD_ID, v_bom.TARGET_GTIN, p_planned_qty, upper(substr(nvl(p_unit_code, v_bom.BASE_UNIT_CODE), 1, 20)),
      p_ware_id, substr(p_production_line, 1, 100), substr(p_shift_id, 1, 50),
      'RELEASED', p_planned_start_at, p_planned_finish_at, substr(p_idempotency_key, 1, 100),
      substr(p_source_system, 1, 50), substr(p_source_message_id, 1, 100),
      substr(p_comment_text, 1, 1000), sysdate, substr(p_created_by, 1, 50)
    );

    v_factor := p_planned_qty / v_bom.BASE_QTY;

    insert into RRL_PROD_ORDER_BOM_LINE (
      ORDER_LINE_ID, PRODUCTION_ORDER_ID, BOM_ID, BOM_LINE_ID, LINE_NO,
      COMPONENT_TYPE, COMPONENT_ARTICUL, COMPONENT_MOD_ID, COMPONENT_NAME,
      PLANNED_QTY, UNIT_CODE, LOSS_PERCENT, IS_REQUIRED, CREATED_AT, CREATED_BY
    )
    select RRL_PROD_ORDER_BOM_LINE_SQ.nextval,
           v_id,
           v_bom_id,
           l.BOM_LINE_ID,
           l.LINE_NO,
           l.COMPONENT_TYPE,
           upper(substr(l.COMPONENT_ARTICUL, 1, 40)),
           l.COMPONENT_MOD_ID,
           l.COMPONENT_NAME,
           round(nvl(l.QTY_PER_BASE, 0) * v_factor * (1 + nvl(l.LOSS_PERCENT, 0) / 100), 6),
           nvl(l.UNIT_CODE, v_bom.BASE_UNIT_CODE),
           nvl(l.LOSS_PERCENT, 0),
           nvl(l.IS_REQUIRED, 1),
           sysdate,
           substr(p_created_by, 1, 50)
      from RRL_BOM_LINE l
     where l.BOM_ID = v_bom_id;

    return v_id;
  end create_order;

  function issue_raw_to_production(
    p_production_order_id number,
    p_uid_pallet          varchar2 default null,
    p_raw_batch_id        number default null,
    p_raw_articul         varchar2 default null,
    p_quantity            number,
    p_unit_code           varchar2 default 'KG',
    p_source_location     varchar2 default null,
    p_production_location varchar2 default 'MES_PRODUCTION',
    p_created_by          varchar2 default null
  ) return number is
    v_id number;
    v_order RRL_PRODUCTION_ORDER%rowtype;
    v_raw_articul varchar2(40);
  begin
    if p_quantity is null or p_quantity <= 0 then
      raise_application_error(-20910, 'issue quantity must be greater than zero');
    end if;

    select * into v_order
      from RRL_PRODUCTION_ORDER
     where PRODUCTION_ORDER_ID = p_production_order_id
       for update;

    if v_order.STATUS in ('COMPLETED', 'CANCELLED') then
      raise_application_error(-20911, 'production order is already closed');
    end if;

    v_raw_articul := upper(substr(p_raw_articul, 1, 40));
    if v_raw_articul is null and p_raw_batch_id is not null then
      select upper(substr(ARTICUL, 1, 40))
        into v_raw_articul
        from RRL_RAW_BATCH
       where RAW_BATCH_ID = p_raw_batch_id;
    end if;

    select RRL_MES_MOVEMENT_SQ.nextval into v_id from dual;

    insert into RRL_MES_MOVEMENT (
      MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, BOM_ID, RAW_BATCH_ID,
      RAW_ARTICUL, UID_PALLET, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
      STATUS, CREATED_AT, CREATED_BY
    ) values (
      v_id, 'RAW_ISSUE_TO_PRODUCTION', p_production_order_id, v_order.BOM_ID, p_raw_batch_id,
      v_raw_articul, substr(p_uid_pallet, 1, 200), p_quantity, upper(substr(p_unit_code, 1, 20)),
      substr(p_source_location, 1, 100), substr(p_production_location, 1, 100),
      'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
    );

    update RRL_PRODUCTION_ORDER
       set STATUS = 'IN_PROGRESS',
           STARTED_AT = nvl(STARTED_AT, sysdate),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PRODUCTION_ORDER_ID = p_production_order_id
       and STATUS in ('DRAFT', 'RELEASED');

    return v_id;
  end issue_raw_to_production;

  function complete_order(
    p_production_order_id number,
    p_prod_batch_no       varchar2 default null,
    p_fact_qty            number,
    p_unit_code           varchar2 default 'KG',
    p_pallets_json        clob default null,
    p_idempotency_key     varchar2 default null,
    p_created_by          varchar2 default null
  ) return number is
    v_completion_id number;
    v_order RRL_PRODUCTION_ORDER%rowtype;
    v_prod_batch_id number;
    v_prod_batch_no varchar2(100);
    v_consumption_count number;
    v_trace_event_id number;
    v_dummy number;
  begin
    if p_idempotency_key is not null then
      begin
        select COMPLETION_ID into v_completion_id
          from RRL_MES_COMPLETION
         where IDEMPOTENCY_KEY = p_idempotency_key;
        return v_completion_id;
      exception
        when no_data_found then null;
      end;
    end if;

    if p_fact_qty is null or p_fact_qty <= 0 then
      raise_application_error(-20920, 'fact quantity must be greater than zero');
    end if;

    select * into v_order
      from RRL_PRODUCTION_ORDER
     where PRODUCTION_ORDER_ID = p_production_order_id
       for update;

    if v_order.STATUS in ('COMPLETED', 'CANCELLED') then
      raise_application_error(-20921, 'production order is already closed');
    end if;

    v_prod_batch_no := substr(nvl(p_prod_batch_no, v_order.ORDER_NO || '-LOT'), 1, 100);

    v_prod_batch_id := RRL_PRODUCTION_API.create_prod_batch(
      p_prod_batch_no => v_prod_batch_no,
      p_articul => v_order.TARGET_ARTICUL,
      p_mod_id => v_order.TARGET_MOD_ID,
      p_gtin => v_order.TARGET_GTIN,
      p_total_quantity => p_fact_qty,
      p_unit_code => nvl(p_unit_code, v_order.UNIT_CODE),
      p_ware_id => v_order.WARE_ID,
      p_source_system => 'MES',
      p_source_message_id => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':COMPLETE'), 1, 100),
      p_production_order_id => v_order.PRODUCTION_ORDER_ID,
      p_produced_date_from => trunc(sysdate),
      p_produced_date_to => trunc(sysdate),
      p_production_line => v_order.PRODUCTION_LINE,
      p_shift_id => v_order.SHIFT_ID,
      p_created_by => p_created_by
    );

    select count(*)
      into v_consumption_count
      from RRL_MES_MOVEMENT
     where PRODUCTION_ORDER_ID = p_production_order_id
       and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
       and STATUS <> 'CANCELLED';

    if v_consumption_count > 0 then
      for r in (
        select RAW_BATCH_ID,
               RAW_ARTICUL,
               UID_PALLET,
               TARGET_LOCATION PRODUCTION_LOCATION,
               sum(QUANTITY) QUANTITY,
               max(UNIT_CODE) UNIT_CODE
          from RRL_MES_MOVEMENT
         where PRODUCTION_ORDER_ID = p_production_order_id
           and MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION'
           and STATUS <> 'CANCELLED'
         group by RAW_BATCH_ID, RAW_ARTICUL, UID_PALLET, TARGET_LOCATION
      ) loop
        v_dummy := RRL_PRODUCTION_API.add_raw_usage(
          p_prod_batch_id => v_prod_batch_id,
          p_raw_batch_id => r.RAW_BATCH_ID,
          p_raw_articul => r.RAW_ARTICUL,
          p_quantity_planned => r.QUANTITY,
          p_quantity_fact => r.QUANTITY,
          p_unit_code => r.UNIT_CODE,
          p_used_by => p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          RAW_BATCH_ID, RAW_ARTICUL, UID_PALLET, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
          STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'RAW_CONSUMPTION', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          r.RAW_BATCH_ID, r.RAW_ARTICUL, r.UID_PALLET, r.QUANTITY, r.UNIT_CODE, nvl(r.PRODUCTION_LOCATION, 'MES_PROD'),
          'MES_FINISHED_GOODS', 'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
        );
      end loop;
    else
      for r in (
        select BOM_LINE_ID, COMPONENT_ARTICUL, PLANNED_QTY, UNIT_CODE
          from RRL_PROD_ORDER_BOM_LINE
         where PRODUCTION_ORDER_ID = p_production_order_id
           and COMPONENT_TYPE in ('RAW', 'SEMIFINISHED', 'PACKAGING', 'ADDITIVE')
      ) loop
        v_dummy := RRL_PRODUCTION_API.add_raw_usage(
          p_prod_batch_id => v_prod_batch_id,
          p_raw_batch_id => null,
          p_raw_articul => r.COMPONENT_ARTICUL,
          p_quantity_planned => r.PLANNED_QTY,
          p_quantity_fact => round(r.PLANNED_QTY * p_fact_qty / v_order.PLANNED_QTY, 6),
          p_unit_code => r.UNIT_CODE,
          p_used_by => p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          BOM_LINE_ID, RAW_ARTICUL, QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION,
          STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'RAW_CONSUMPTION', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          r.BOM_LINE_ID, r.COMPONENT_ARTICUL, round(r.PLANNED_QTY * p_fact_qty / v_order.PLANNED_QTY, 6),
          r.UNIT_CODE, 'MES_PRODUCTION', 'MES_FINISHED_GOODS', 'MES_POSTED', sysdate,
          substr(p_created_by, 1, 50)
        );
      end loop;
    end if;

    select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
    insert into RRL_MES_MOVEMENT (
      MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
      QUANTITY, UNIT_CODE, SOURCE_LOCATION, TARGET_LOCATION, STATUS, CREATED_AT, CREATED_BY
    ) values (
      v_dummy, 'FG_LOT_RELEASE', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
      p_fact_qty, nvl(p_unit_code, v_order.UNIT_CODE), 'MES_PRODUCTION', 'MES_FINISHED_GOODS',
      'MES_POSTED', sysdate, substr(p_created_by, 1, 50)
    );

    if p_pallets_json is not null then
      for p in (
        select uid_pallet, pallet_no, quantity, pack_count, sscc
          from json_table(
            p_pallets_json,
            '$[*]' columns (
              uid_pallet varchar2(200) path '$.uid_pallet',
              pallet_no number path '$.pallet_no',
              quantity number path '$.quantity',
              pack_count number path '$.pack_count',
              sscc varchar2(50) path '$.sscc'
            )
          )
      ) loop
        if p.uid_pallet is null then
          raise_application_error(-20922, 'pallet uid is required');
        end if;

        merge into RRL_PROD_BATCH_PALLETS d
        using (
          select v_prod_batch_id PROD_BATCH_ID,
                 p.uid_pallet UID_PALLET
            from dual
        ) s
        on (d.PROD_BATCH_ID = s.PROD_BATCH_ID and d.UID_PALLET = s.UID_PALLET)
        when matched then update set
          d.PALLET_NO = nvl(p.pallet_no, d.PALLET_NO),
          d.QUANTITY = nvl(p.quantity, d.QUANTITY),
          d.PACK_COUNT = nvl(p.pack_count, d.PACK_COUNT),
          d.SSCC = nvl(p.sscc, d.SSCC)
        when not matched then insert (
          PROD_BATCH_ID, UID_PALLET, PALLET_NO, QUANTITY, PACK_COUNT,
          SSCC, AGGREGATION_STATUS, CREATED_AT, CREATED_BY
        ) values (
          v_prod_batch_id, p.uid_pallet, p.pallet_no, p.quantity, p.pack_count,
          p.sscc, 'DRAFT', sysdate, p_created_by
        );

        select RRL_MES_MOVEMENT_SQ.nextval into v_dummy from dual;
        insert into RRL_MES_MOVEMENT (
          MOVEMENT_ID, MOVEMENT_TYPE, PRODUCTION_ORDER_ID, PROD_BATCH_ID, BOM_ID,
          UID_PALLET, SSCC, QUANTITY, PACK_COUNT, UNIT_CODE, SOURCE_LOCATION,
          TARGET_LOCATION, STATUS, PAYLOAD_JSON, CREATED_AT, CREATED_BY
        ) values (
          v_dummy, 'FG_PALLET_RELEASE', p_production_order_id, v_prod_batch_id, v_order.BOM_ID,
          substr(p.uid_pallet, 1, 200), substr(p.sscc, 1, 50), p.quantity, p.pack_count,
          nvl(p_unit_code, v_order.UNIT_CODE), 'MES_PRODUCTION', 'MES_FG',
          'MES_POSTED',
          '{"uid_pallet":"' || replace(substr(p.uid_pallet, 1, 200), '"', '\"') || '"}',
          sysdate, substr(p_created_by, 1, 50)
        );
      end loop;
    end if;

    select RRL_MES_COMPLETION_SQ.nextval into v_completion_id from dual;
    insert into RRL_MES_COMPLETION (
      COMPLETION_ID, PRODUCTION_ORDER_ID, PROD_BATCH_ID, IDEMPOTENCY_KEY,
      STATUS, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      v_completion_id, p_production_order_id, v_prod_batch_id,
      substr(p_idempotency_key, 1, 100), 'DONE', p_pallets_json, sysdate,
      substr(p_created_by, 1, 50)
    );

    update RRL_PRODUCTION_ORDER
       set STATUS = 'COMPLETED',
           FACT_QTY = p_fact_qty,
           COMPLETED_AT = sysdate,
           PROD_BATCH_ID = v_prod_batch_id,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PRODUCTION_ORDER_ID = p_production_order_id;

    update RRL_PROD_BATCH
       set QUALITY_STATUS = 'RELEASED',
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_created_by, 1, 50)
     where PROD_BATCH_ID = v_prod_batch_id;

    v_trace_event_id := RRL_TRACEABILITY_API.add_trace_event(
      p_event_type => 'PRODUCTION_COMPLETED',
      p_entity_type => 'PRODUCTION_ORDER',
      p_entity_id => to_char(p_production_order_id),
      p_source_system => 'MES',
      p_correlation_id => v_order.ORDER_NO,
      p_idempotency_key => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':TRACE'), 1, 100),
      p_payload_json => p_pallets_json,
      p_created_by => p_created_by
    );

    v_dummy := RRL_TRACEABILITY_API.add_trace_edge(
      p_from_entity_type => 'PRODUCTION_ORDER',
      p_from_entity_id => to_char(p_production_order_id),
      p_to_entity_type => 'FINISHED_GOODS_LOT',
      p_to_entity_id => to_char(v_prod_batch_id),
      p_edge_type => 'PRODUCES',
      p_quantity => p_fact_qty,
      p_unit_code => nvl(p_unit_code, v_order.UNIT_CODE),
      p_trace_event_id => v_trace_event_id,
      p_created_by => p_created_by
    );

    v_dummy := RRL_TRACEABILITY_API.enqueue_event(
      p_event_type => 'PRODUCTION_COMPLETED',
      p_aggregate_type => 'PRODUCTION_ORDER',
      p_aggregate_id => to_char(p_production_order_id),
      p_idempotency_key => substr(nvl(p_idempotency_key, v_order.ORDER_NO || ':OUTBOX'), 1, 100),
      p_payload_json => p_pallets_json,
      p_target_system => 'TRACEABILITY',
      p_correlation_id => v_order.ORDER_NO
    );

    return v_completion_id;
  end complete_order;

  procedure apply_mes_movements_to_wms(
    p_production_order_id number,
    p_applied_by          varchar2 default null
  ) is
    v_event_id number;
    v_error varchar2(4000);
  begin
    for m in (
      select *
        from RRL_MES_MOVEMENT
       where PRODUCTION_ORDER_ID = p_production_order_id
         and STATUS in ('MES_POSTED', 'ERROR')
         and MOVEMENT_TYPE in ('RAW_ISSUE_TO_PRODUCTION', 'RAW_CONSUMPTION', 'FG_PALLET_RELEASE')
       order by MOVEMENT_ID
    ) loop
      begin
        if m.UID_PALLET is null then
          raise_application_error(-20940, 'legacy WMS event requires UID_PALLET');
        end if;

        if m.MOVEMENT_TYPE = 'FG_PALLET_RELEASE' then
          merge into RRL_PALLETS d
          using (
            select m.UID_PALLET UID_PALLET,
                   o.TARGET_ARTICUL ARTICUL,
                   m.QUANTITY UNIT_COUNT,
                   m.PROD_BATCH_ID PROD_BATCH_ID,
                   m.SSCC SSCC
              from RRL_PRODUCTION_ORDER o
             where o.PRODUCTION_ORDER_ID = p_production_order_id
          ) s
          on (d.UID_PALLET = s.UID_PALLET)
          when matched then update set
            d.ARTICUL = nvl(s.ARTICUL, d.ARTICUL),
            d.UNIT_COUNT = nvl(s.UNIT_COUNT, d.UNIT_COUNT),
            d.PROD_BATCH_ID = nvl(s.PROD_BATCH_ID, d.PROD_BATCH_ID),
            d.SSCC = nvl(s.SSCC, d.SSCC),
            d.QUALITY_STATUS = 'RELEASED'
          when not matched then insert (
            UID_PALLET, ARTICUL, UNIT_COUNT, PRIHOD_NAKLAD_ID,
            PROD_BATCH_ID, SSCC, QUALITY_STATUS
          ) values (
            s.UID_PALLET, s.ARTICUL, s.UNIT_COUNT, 0,
            s.PROD_BATCH_ID, s.SSCC, 'RELEASED'
          );
        end if;

        select RRL_EVENT_ID_SQ.nextval into v_event_id from dual;

        if m.MOVEMENT_TYPE = 'RAW_ISSUE_TO_PRODUCTION' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'UNKNOWN'), 1, 20),
            substr(nvl(m.TARGET_LOCATION, 'MES_PROD'), 1, 20), sysdate,
            nvl(m.QUANTITY, 0), 2, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        elsif m.MOVEMENT_TYPE = 'RAW_CONSUMPTION' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'MES_PROD'), 1, 20),
            'none', sysdate, nvl(m.QUANTITY, 0), 3, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        elsif m.MOVEMENT_TYPE = 'FG_PALLET_RELEASE' then
          insert into RRL_EVENTS (
            ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
            TYPE_EVENT, UID_POLETA, USER_ID
          ) values (
            v_event_id, substr(nvl(m.SOURCE_LOCATION, 'MES_PROD'), 1, 20),
            substr(nvl(m.TARGET_LOCATION, 'MES_FG'), 1, 20), sysdate,
            nvl(m.QUANTITY, 0), 1, substr(m.UID_PALLET, 1, 200),
            substr(nvl(p_applied_by, user), 1, 50)
          );
        else
          raise_application_error(-20941, 'movement type is not supported by legacy WMS bridge');
        end if;

        update RRL_MES_MOVEMENT
           set STATUS = 'APPLIED_TO_WMS',
               WMS_APPLIED_AT = sysdate,
               WMS_APPLIED_BY = substr(p_applied_by, 1, 50),
               LAST_ERROR = null,
               UPDATED_AT = sysdate,
               UPDATED_BY = substr(p_applied_by, 1, 50)
         where MOVEMENT_ID = m.MOVEMENT_ID;
      exception
        when others then
          v_error := sqlerrm;
          update RRL_MES_MOVEMENT
             set STATUS = 'ERROR',
                 RETRY_COUNT = RETRY_COUNT + 1,
                 LAST_ERROR = substr(v_error, 1, 4000),
                 UPDATED_AT = sysdate,
                 UPDATED_BY = substr(p_applied_by, 1, 50)
           where MOVEMENT_ID = m.MOVEMENT_ID;
      end;
    end loop;
  end apply_mes_movements_to_wms;

  procedure retry_mes_movement(
    p_movement_id number,
    p_updated_by  varchar2 default null
  ) is
  begin
    update RRL_MES_MOVEMENT
       set STATUS = 'MES_POSTED',
           LAST_ERROR = null,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where MOVEMENT_ID = p_movement_id
       and STATUS = 'ERROR';

    if sql%rowcount = 0 then
      raise_application_error(-20930, 'MES movement is not in ERROR status');
    end if;
  end retry_mes_movement;
end RRL_MES_PRODUCTION_API;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'MES_PRODUCTION_VIEW' RIGHT1, 'View MES production orders and movement journal' DESCR from dual
    union all
    select 'MES_PRODUCTION_EDIT', 'Create MES production orders and issue raw material' from dual
    union all
    select 'MES_PRODUCTION_COMPLETE', 'Complete MES production orders and release finished goods pallets' from dual
    union all
    select 'MES_WMS_BRIDGE_APPLY', 'Apply MES movements to legacy WMS bridge' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-011-mes-production-completion' migration_id,
         'MES production orders, movement journal, completion API, and controlled WMS bridge' description,
         '011_apply.sql' script_name,
         '011_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set
  d.DESCRIPTION = s.DESCRIPTION,
  d.SCRIPT_NAME = s.SCRIPT_NAME,
  d.ROLLBACK_SCRIPT = s.ROLLBACK_SCRIPT,
  d.APPLIED_AT = sysdate,
  d.APPLIED_BY = user
when not matched then insert (
  MIGRATION_ID, DESCRIPTION, SCRIPT_NAME, ROLLBACK_SCRIPT, APPLIED_AT, APPLIED_BY
) values (
  s.MIGRATION_ID, s.DESCRIPTION, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, sysdate, user
);

commit;

prompt [migration 2026-05-17-011] done
