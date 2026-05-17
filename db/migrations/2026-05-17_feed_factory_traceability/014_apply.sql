prompt [migration 2026-05-17-014] Customer and order foundation - apply

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
begin
  ensure_table('RRL_CUSTOMER', q'[
    create table RRL_CUSTOMER (
      CUSTOMER_ID number not null,
      CUSTOMER_CODE varchar2(100) not null,
      CUSTOMER_NAME varchar2(255) not null,
      CUSTOMER_TYPE varchar2(30) default 'STORE' not null,
      INN varchar2(20),
      KPP varchar2(20),
      GLN varchar2(32),
      EDI_ID varchar2(100),
      DEFAULT_VEHICLE_TYPE_ID number,
      SPLIT_ORDER_BY_VEHICLE_CAPACITY number(1) default 0 not null,
      DEFAULT_MIN_SHELF_LIFE_DAYS number,
      DEFAULT_MIN_SHELF_LIFE_PERCENT number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUSTOMER_PK primary key (CUSTOMER_ID),
      constraint RRL_CUSTOMER_U1 unique (CUSTOMER_CODE),
      constraint RRL_CUSTOMER_CHK1 check (CUSTOMER_TYPE in ('STORE', 'CHAIN', 'DISTRIBUTOR', 'LEGAL_ENTITY', 'OTHER')),
      constraint RRL_CUSTOMER_CHK2 check (ACTIVE in (0, 1)),
      constraint RRL_CUSTOMER_CHK3 check (SPLIT_ORDER_BY_VEHICLE_CAPACITY in (0, 1)),
      constraint RRL_CUSTOMER_CHK4 check (DEFAULT_MIN_SHELF_LIFE_PERCENT is null or (DEFAULT_MIN_SHELF_LIFE_PERCENT >= 0 and DEFAULT_MIN_SHELF_LIFE_PERCENT <= 100))
    )
  ]');

  ensure_table('RRL_CUSTOMER_ADDRESS', q'[
    create table RRL_CUSTOMER_ADDRESS (
      CUSTOMER_ADDRESS_ID number not null,
      CUSTOMER_ID number not null,
      ADDRESS_TYPE varchar2(30) default 'DELIVERY' not null,
      ADDRESS_TEXT varchar2(1000) not null,
      CITY varchar2(100),
      REGION varchar2(100),
      POSTAL_CODE varchar2(20),
      GLN varchar2(32),
      LATITUDE number,
      LONGITUDE number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUSTOMER_ADDRESS_PK primary key (CUSTOMER_ADDRESS_ID),
      constraint RRL_CUSTOMER_ADDRESS_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CUSTOMER_ADDRESS_CHK1 check (ADDRESS_TYPE in ('LEGAL', 'DELIVERY', 'BILLING', 'STORE')),
      constraint RRL_CUSTOMER_ADDRESS_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_CUSTOMER_STORE_MAP', q'[
    create table RRL_CUSTOMER_STORE_MAP (
      CUSTOMER_STORE_MAP_ID number not null,
      CUSTOMER_ID number not null,
      LEGACY_ADDR varchar2(255),
      LEGACY_ADDR_KEY varchar2(255) not null,
      STORE_CODE varchar2(100),
      STORE_NAME varchar2(255),
      ADDRESS_TEXT varchar2(1000),
      CITY varchar2(100),
      REGION varchar2(100),
      GLN varchar2(32),
      EDI_ID varchar2(100),
      DEFAULT_ROUTE_ID number,
      DEFAULT_DOCK_ID number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUSTOMER_STORE_MAP_PK primary key (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CUSTOMER_STORE_MAP_U1 unique (LEGACY_ADDR_KEY),
      constraint RRL_CUSTOMER_STORE_MAP_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CUSTOMER_STORE_MAP_CHK1 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_CUSTOMER_ORDER', q'[
    create table RRL_CUSTOMER_ORDER (
      CUSTOMER_ORDER_ID number not null,
      LEGACY_ORDER_ID number,
      ORDER_NO varchar2(100) not null,
      CUSTOMER_ID number not null,
      CUSTOMER_STORE_MAP_ID number,
      WARE_ID number,
      ORDER_DATE date,
      SHIPMENT_DATE date,
      ROUTE_ID number,
      DOCK_ID number,
      STATUS varchar2(30) default 'IMPORTED' not null,
      SOURCE_SYSTEM varchar2(50) default 'LEGACY_WMS' not null,
      SOURCE_CREATED_BY varchar2(50),
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUSTOMER_ORDER_PK primary key (CUSTOMER_ORDER_ID),
      constraint RRL_CUSTOMER_ORDER_U1 unique (LEGACY_ORDER_ID),
      constraint RRL_CUSTOMER_ORDER_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CUSTOMER_ORDER_FK2 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CUSTOMER_ORDER_CHK1 check (STATUS in ('DRAFT', 'IMPORTED', 'OPEN', 'PLANNED_FULL', 'PLANNED_PARTIAL', 'NO_STOCK', 'IN_WAVE', 'PICKING', 'FULFILLED', 'CANCELLED'))
    )
  ]');

  ensure_table('RRL_CUSTOMER_ORDER_ROW', q'[
    create table RRL_CUSTOMER_ORDER_ROW (
      CUSTOMER_ORDER_ROW_ID number not null,
      CUSTOMER_ORDER_ID number not null,
      LEGACY_ORDER_ROW_ID number,
      LINE_NO number not null,
      ARTICUL varchar2(40) not null,
      PRODUCT_NAME varchar2(255),
      UNIT_CODE varchar2(20),
      ORDER_QTY number not null,
      ORDER_WEIGHT number,
      PACK_COUNT number,
      WARE_ID number,
      MOD_ID number,
      SORTFIELD number,
      CONDITION_CODE number,
      STATUS varchar2(30) default 'OPEN' not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUSTOMER_ORDER_ROW_PK primary key (CUSTOMER_ORDER_ROW_ID),
      constraint RRL_CUSTOMER_ORDER_ROW_U1 unique (LEGACY_ORDER_ROW_ID),
      constraint RRL_CUSTOMER_ORDER_ROW_FK1 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_CUSTOMER_ORDER_ROW_CHK1 check (ORDER_QTY >= 0),
      constraint RRL_CUSTOMER_ORDER_ROW_CHK2 check (STATUS in ('OPEN', 'PLANNED_FULL', 'PLANNED_PARTIAL', 'NO_STOCK', 'PICKING', 'FULFILLED', 'CANCELLED'))
    )
  ]');

  ensure_table('RRL_CUSTOMER_ORDER_FULFILLMENT', q'[
    create table RRL_CUSTOMER_ORDER_FULFILLMENT (
      FULFILLMENT_ID number not null,
      CUSTOMER_ORDER_ID number not null,
      LEGACY_SBORKA_PALLET_ID number,
      PALLET_UID varchar2(100),
      ADDRESS_TEXT varchar2(1000),
      STATUS varchar2(30) default 'LEGACY_FACT' not null,
      FACT_QTY number,
      FACT_WEIGHT number,
      SOURCE_SYSTEM varchar2(50) default 'LEGACY_WMS' not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CUST_ORDER_FULF_PK primary key (FULFILLMENT_ID),
      constraint RRL_CUST_ORDER_FULF_U1 unique (CUSTOMER_ORDER_ID, LEGACY_SBORKA_PALLET_ID),
      constraint RRL_CUST_ORDER_FULF_FK1 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_CUST_ORDER_FULF_CHK1 check (STATUS in ('LEGACY_FACT', 'PICKED', 'SHIPPED', 'CANCELLED'))
    )
  ]');

  ensure_sequence('RRL_CUSTOMER_SQ', 'create sequence RRL_CUSTOMER_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUSTOMER_ADDRESS_SQ', 'create sequence RRL_CUSTOMER_ADDRESS_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUSTOMER_STORE_MAP_SQ', 'create sequence RRL_CUSTOMER_STORE_MAP_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUSTOMER_ORDER_SQ', 'create sequence RRL_CUSTOMER_ORDER_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUSTOMER_ORDER_ROW_SQ', 'create sequence RRL_CUSTOMER_ORDER_ROW_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CUSTOMER_ORDER_FULF_SQ', 'create sequence RRL_CUSTOMER_ORDER_FULF_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_CUSTOMER_I1', 'create index RRL_CUSTOMER_I1 on RRL_CUSTOMER (CUSTOMER_NAME)');
  ensure_index('RRL_CUSTOMER_ADDRESS_I1', 'create index RRL_CUSTOMER_ADDRESS_I1 on RRL_CUSTOMER_ADDRESS (CUSTOMER_ID, ADDRESS_TYPE, ACTIVE)');
  ensure_index('RRL_CUSTOMER_STORE_MAP_I1', 'create index RRL_CUSTOMER_STORE_MAP_I1 on RRL_CUSTOMER_STORE_MAP (CUSTOMER_ID, ACTIVE)');
  ensure_index('RRL_CUSTOMER_ORDER_I1', 'create index RRL_CUSTOMER_ORDER_I1 on RRL_CUSTOMER_ORDER (CUSTOMER_ID, STATUS, SHIPMENT_DATE)');
  ensure_index('RRL_CUSTOMER_ORDER_I2', 'create index RRL_CUSTOMER_ORDER_I2 on RRL_CUSTOMER_ORDER (ORDER_NO)');
  ensure_index('RRL_CUSTOMER_ORDER_ROW_I1', 'create index RRL_CUSTOMER_ORDER_ROW_I1 on RRL_CUSTOMER_ORDER_ROW (CUSTOMER_ORDER_ID, LINE_NO)');
  ensure_index('RRL_CUSTOMER_ORDER_ROW_I2', 'create index RRL_CUSTOMER_ORDER_ROW_I2 on RRL_CUSTOMER_ORDER_ROW (ARTICUL, STATUS)');
  ensure_index('RRL_CUST_ORDER_FULF_I1', 'create index RRL_CUST_ORDER_FULF_I1 on RRL_CUSTOMER_ORDER_FULFILLMENT (CUSTOMER_ORDER_ID, STATUS)');
  ensure_index('RRL_CUST_ORDER_FULF_I2', 'create index RRL_CUST_ORDER_FULF_I2 on RRL_CUSTOMER_ORDER_FULFILLMENT (PALLET_UID)');
end;
/

create or replace package RRL_CUSTOMER_ORDER_API as
  function normalize_key(p_value varchar2) return varchar2 deterministic;

  function ensure_customer_from_legacy_addr(
    p_legacy_addr varchar2,
    p_created_by  varchar2 default null
  ) return number;

  function import_legacy_order(
    p_legacy_order_id number,
    p_created_by      varchar2 default null
  ) return number;

  procedure sync_fulfillment_from_legacy(
    p_customer_order_id number,
    p_created_by        varchar2 default null
  );
end RRL_CUSTOMER_ORDER_API;
/

create or replace package body RRL_CUSTOMER_ORDER_API as
  function normalize_key(p_value varchar2) return varchar2 deterministic is
    v_value varchar2(255);
  begin
    v_value := regexp_replace(upper(trim(nvl(p_value, 'NO_ADDRESS'))), '[[:space:]]+', ' ');
    return substr(v_value, 1, 255);
  end normalize_key;

  function ensure_customer_from_legacy_addr(
    p_legacy_addr varchar2,
    p_created_by  varchar2 default null
  ) return number is
    v_key varchar2(255);
    v_customer_id number;
    v_store_map_id number;
    v_addr varchar2(255);
  begin
    v_key := normalize_key(p_legacy_addr);
    v_addr := substr(nvl(p_legacy_addr, 'NO_ADDRESS'), 1, 255);

    begin
      select CUSTOMER_ID
        into v_customer_id
        from RRL_CUSTOMER_STORE_MAP
       where LEGACY_ADDR_KEY = v_key
         and ACTIVE = 1;
      return v_customer_id;
    exception
      when no_data_found then
        null;
    end;

    select RRL_CUSTOMER_SQ.nextval into v_customer_id from dual;

    insert into RRL_CUSTOMER (
      CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE,
      ACTIVE, CREATED_AT, CREATED_BY
    ) values (
      v_customer_id,
      'LEGACY_ADDR_' || to_char(v_customer_id),
      v_addr,
      'STORE',
      1,
      sysdate,
      substr(p_created_by, 1, 50)
    );

    insert into RRL_CUSTOMER_ADDRESS (
      CUSTOMER_ADDRESS_ID, CUSTOMER_ID, ADDRESS_TYPE, ADDRESS_TEXT,
      ACTIVE, CREATED_AT, CREATED_BY
    ) values (
      RRL_CUSTOMER_ADDRESS_SQ.nextval,
      v_customer_id,
      'DELIVERY',
      v_addr,
      1,
      sysdate,
      substr(p_created_by, 1, 50)
    );

    select RRL_CUSTOMER_STORE_MAP_SQ.nextval into v_store_map_id from dual;
    insert into RRL_CUSTOMER_STORE_MAP (
      CUSTOMER_STORE_MAP_ID, CUSTOMER_ID, LEGACY_ADDR, LEGACY_ADDR_KEY,
      STORE_CODE, STORE_NAME, ADDRESS_TEXT, ACTIVE, CREATED_AT, CREATED_BY
    ) values (
      v_store_map_id,
      v_customer_id,
      v_addr,
      v_key,
      'LEGACY_ADDR_' || to_char(v_customer_id),
      v_addr,
      v_addr,
      1,
      sysdate,
      substr(p_created_by, 1, 50)
    );

    return v_customer_id;
  end ensure_customer_from_legacy_addr;

  procedure sync_fulfillment_from_legacy(
    p_customer_order_id number,
    p_created_by        varchar2 default null
  ) is
    v_order_no varchar2(100);
  begin
    select ORDER_NO
      into v_order_no
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = p_customer_order_id;

    insert into RRL_CUSTOMER_ORDER_FULFILLMENT (
      FULFILLMENT_ID, CUSTOMER_ORDER_ID, LEGACY_SBORKA_PALLET_ID,
      PALLET_UID, ADDRESS_TEXT, STATUS, FACT_QTY, FACT_WEIGHT,
      SOURCE_SYSTEM, CREATED_AT, CREATED_BY
    )
    select RRL_CUSTOMER_ORDER_FULF_SQ.nextval,
           p_customer_order_id,
           src.ID,
           src.PALLET_UID,
           src.ADDR,
           'LEGACY_FACT',
           src.FACT_QTY,
           src.FACT_WEIGHT,
           'LEGACY_WMS',
           sysdate,
           substr(p_created_by, 1, 50)
      from (
        select sp.ID,
               sp.PALLET_UID,
               sp.ADDR,
               sum(nvl(spr.QUANTITY, 0)) FACT_QTY,
               sum(nvl(spr.ORDER_WEIGHT, 0)) FACT_WEIGHT
          from RRL_SBORKA_PALLETS sp
          left join RRL_SBORKA_PALLET_ROWS spr
            on spr.PALLET_UID = sp.PALLET_UID
         where sp.ID is not null
           and (
                sp.ORIGINAL_ORDER_NUMBER = v_order_no
             or sp.ST_NUMBER = v_order_no
             or sp.ORIGINAL_ST_NUMBER = v_order_no
             or sp.NAKLAD_NUMBER = v_order_no
           )
           and not exists (
             select 1
               from RRL_CUSTOMER_ORDER_FULFILLMENT f
              where f.CUSTOMER_ORDER_ID = p_customer_order_id
                and f.LEGACY_SBORKA_PALLET_ID = sp.ID
           )
         group by sp.ID, sp.PALLET_UID, sp.ADDR
      ) src;
  end sync_fulfillment_from_legacy;

  function import_legacy_order(
    p_legacy_order_id number,
    p_created_by      varchar2 default null
  ) return number is
    v_order RRL_ORDERS%rowtype;
    v_customer_id number;
    v_store_map_id number;
    v_customer_order_id number;
  begin
    begin
      select CUSTOMER_ORDER_ID
        into v_customer_order_id
        from RRL_CUSTOMER_ORDER
       where LEGACY_ORDER_ID = p_legacy_order_id;

      sync_fulfillment_from_legacy(v_customer_order_id, p_created_by);
      return v_customer_order_id;
    exception
      when no_data_found then
        null;
    end;

    select *
      into v_order
      from RRL_ORDERS
     where ID = p_legacy_order_id;

    v_customer_id := ensure_customer_from_legacy_addr(v_order.ADDR, p_created_by);

    select CUSTOMER_STORE_MAP_ID
      into v_store_map_id
      from RRL_CUSTOMER_STORE_MAP
     where LEGACY_ADDR_KEY = normalize_key(v_order.ADDR)
       and ACTIVE = 1;

    select RRL_CUSTOMER_ORDER_SQ.nextval into v_customer_order_id from dual;

    insert into RRL_CUSTOMER_ORDER (
      CUSTOMER_ORDER_ID, LEGACY_ORDER_ID, ORDER_NO, CUSTOMER_ID,
      CUSTOMER_STORE_MAP_ID, WARE_ID, ORDER_DATE, SHIPMENT_DATE,
      STATUS, SOURCE_SYSTEM, SOURCE_CREATED_BY, CREATED_AT, CREATED_BY
    ) values (
      v_customer_order_id,
      v_order.ID,
      substr(v_order.ORD_NUMBER, 1, 100),
      v_customer_id,
      v_store_map_id,
      v_order.WARE_ID,
      v_order.CREATE_DATE,
      v_order.ORDDATE,
      'IMPORTED',
      'LEGACY_WMS',
      substr(v_order.USER_ID, 1, 50),
      sysdate,
      substr(p_created_by, 1, 50)
    );

    insert into RRL_CUSTOMER_ORDER_ROW (
      CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LEGACY_ORDER_ROW_ID,
      LINE_NO, ARTICUL, PRODUCT_NAME, UNIT_CODE, ORDER_QTY, ORDER_WEIGHT,
      PACK_COUNT, WARE_ID, MOD_ID, SORTFIELD, CONDITION_CODE,
      STATUS, CREATED_AT, CREATED_BY
    )
    select RRL_CUSTOMER_ORDER_ROW_SQ.nextval,
           v_customer_order_id,
           r.ID,
           row_number() over (order by nvl(r.SORTFIELD, r.ID), r.ID) * 10,
           upper(substr(r.ARTICUL, 1, 40)),
           substr(r.SHORTNAME, 1, 255),
           upper(substr(r.EI, 1, 20)),
           nvl(r.QUANTITY, 0),
           r.ORDER_WEIGHT,
           r.PACK_COUNT,
           r.WARE_ID,
           r.MOD_ID,
           r.SORTFIELD,
           r.CONDITION,
           'OPEN',
           sysdate,
           substr(p_created_by, 1, 50)
      from RRL_ORDER_ROWS r
     where r.ORDER_ID = p_legacy_order_id;

    sync_fulfillment_from_legacy(v_customer_order_id, p_created_by);

    return v_customer_order_id;
  exception
    when no_data_found then
      raise_application_error(-20960, 'legacy order not found');
  end import_legacy_order;
end RRL_CUSTOMER_ORDER_API;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'CUSTOMER_VIEW' RIGHT1, 'View customer registry' DESCR from dual
    union all
    select 'CUSTOMER_EDIT', 'Edit customer registry' from dual
    union all
    select 'CUSTOMER_ORDER_VIEW', 'View customer orders' from dual
    union all
    select 'CUSTOMER_ORDER_IMPORT', 'Import legacy WMS orders into customer-order model' from dual
    union all
    select 'CUSTOMER_FULFILLMENT_VIEW', 'View customer order fulfillment fact' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-014-customer-order-foundation' migration_id,
         'Customer registry, legacy store mapping, customer orders, rows, and fulfillment foundation' description,
         '014_apply.sql' script_name,
         '014_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-014] done
