prompt [migration 2026-05-17-015] Customer rules and vehicle capacity - apply

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
  ensure_table('RRL_CUSTOMER_SHELF_LIFE_RULE', q'[
    create table RRL_CUSTOMER_SHELF_LIFE_RULE (
      SHELF_LIFE_RULE_ID number not null,
      CUSTOMER_ID number not null,
      CUSTOMER_STORE_MAP_ID number,
      ARTICUL varchar2(40),
      PRODUCT_GROUP varchar2(100),
      MIN_SHELF_LIFE_DAYS number,
      MIN_SHELF_LIFE_PERCENT number,
      RULE_PRIORITY number default 100 not null,
      ACTIVE number(1) default 1 not null,
      VALID_FROM date default trunc(sysdate) not null,
      VALID_TO date,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CSL_RULE_PK primary key (SHELF_LIFE_RULE_ID),
      constraint RRL_CSL_RULE_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CSL_RULE_FK2 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CSL_RULE_CHK1 check (ACTIVE in (0, 1)),
      constraint RRL_CSL_RULE_CHK2 check (MIN_SHELF_LIFE_PERCENT is null or (MIN_SHELF_LIFE_PERCENT >= 0 and MIN_SHELF_LIFE_PERCENT <= 100)),
      constraint RRL_CSL_RULE_CHK3 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_table('RRL_CUSTOMER_PRODUCT_STACK_RULE', q'[
    create table RRL_CUSTOMER_PRODUCT_STACK_RULE (
      STACK_RULE_ID number not null,
      CUSTOMER_ID number not null,
      CUSTOMER_STORE_MAP_ID number,
      ARTICUL varchar2(40),
      PRODUCT_GROUP varchar2(100),
      PALLET_CASE_QTY number,
      PALLET_LAYER_QTY number,
      PALLET_LAYER_COUNT number,
      MAX_PALLET_WEIGHT number,
      MAX_PALLET_VOLUME number,
      MAX_PALLET_HEIGHT number,
      PALLET_TYPE varchar2(50),
      ALLOW_TOP_STACKING number(1) default 0 not null,
      MUST_BE_SEPARATE_PALLET number(1) default 0 not null,
      STACK_COMPATIBILITY_GROUP varchar2(100),
      RULE_PRIORITY number default 100 not null,
      ACTIVE number(1) default 1 not null,
      VALID_FROM date default trunc(sysdate) not null,
      VALID_TO date,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CPS_RULE_PK primary key (STACK_RULE_ID),
      constraint RRL_CPS_RULE_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CPS_RULE_FK2 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CPS_RULE_CHK1 check (ACTIVE in (0, 1)),
      constraint RRL_CPS_RULE_CHK2 check (ALLOW_TOP_STACKING in (0, 1)),
      constraint RRL_CPS_RULE_CHK3 check (MUST_BE_SEPARATE_PALLET in (0, 1)),
      constraint RRL_CPS_RULE_CHK4 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_table('RRL_VEHICLE_TYPE', q'[
    create table RRL_VEHICLE_TYPE (
      VEHICLE_TYPE_ID number not null,
      VEHICLE_TYPE_CODE varchar2(50) not null,
      VEHICLE_TYPE_NAME varchar2(255) not null,
      MAX_PALLET_COUNT number,
      MAX_WEIGHT number,
      MAX_VOLUME number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_VEHICLE_TYPE_PK primary key (VEHICLE_TYPE_ID),
      constraint RRL_VEHICLE_TYPE_U1 unique (VEHICLE_TYPE_CODE),
      constraint RRL_VEHICLE_TYPE_CHK1 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_CUSTOMER_VEHICLE_RULE', q'[
    create table RRL_CUSTOMER_VEHICLE_RULE (
      CUSTOMER_VEHICLE_RULE_ID number not null,
      CUSTOMER_ID number not null,
      CUSTOMER_STORE_MAP_ID number,
      VEHICLE_TYPE_ID number not null,
      MAX_PALLET_COUNT number,
      MAX_WEIGHT number,
      MAX_VOLUME number,
      SPLIT_ORDER_BY_CAPACITY number(1) default 1 not null,
      RULE_PRIORITY number default 100 not null,
      ACTIVE number(1) default 1 not null,
      VALID_FROM date default trunc(sysdate) not null,
      VALID_TO date,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_CVR_PK primary key (CUSTOMER_VEHICLE_RULE_ID),
      constraint RRL_CVR_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CVR_FK2 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CVR_FK3 foreign key (VEHICLE_TYPE_ID) references RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID),
      constraint RRL_CVR_CHK1 check (ACTIVE in (0, 1)),
      constraint RRL_CVR_CHK2 check (SPLIT_ORDER_BY_CAPACITY in (0, 1)),
      constraint RRL_CVR_CHK3 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_table('RRL_SHIPMENT_PART', q'[
    create table RRL_SHIPMENT_PART (
      SHIPMENT_PART_ID number not null,
      CUSTOMER_ORDER_ID number not null,
      PICK_PLAN_ID number,
      ROUTE_ID number,
      DOCK_ID number,
      VEHICLE_TYPE_ID number,
      PART_NO number not null,
      PLANNED_PALLET_COUNT number,
      PLANNED_WEIGHT number,
      PLANNED_VOLUME number,
      STATUS varchar2(30) default 'PLANNED' not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_SHIPMENT_PART_PK primary key (SHIPMENT_PART_ID),
      constraint RRL_SHIPMENT_PART_U1 unique (CUSTOMER_ORDER_ID, PART_NO),
      constraint RRL_SHIPMENT_PART_FK1 foreign key (CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER (CUSTOMER_ORDER_ID),
      constraint RRL_SHIPMENT_PART_FK2 foreign key (VEHICLE_TYPE_ID) references RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID),
      constraint RRL_SHIPMENT_PART_CHK1 check (STATUS in ('PLANNED', 'IN_PICKING', 'READY', 'SHIPPED', 'CANCELLED')),
      constraint RRL_SHIPMENT_PART_CHK2 check (PLANNED_PALLET_COUNT is null or PLANNED_PALLET_COUNT >= 0)
    )
  ]');

  ensure_sequence('RRL_CSL_RULE_SQ', 'create sequence RRL_CSL_RULE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CPS_RULE_SQ', 'create sequence RRL_CPS_RULE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_VEHICLE_TYPE_SQ', 'create sequence RRL_VEHICLE_TYPE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_CVR_SQ', 'create sequence RRL_CVR_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_SHIPMENT_PART_SQ', 'create sequence RRL_SHIPMENT_PART_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_CSL_RULE_I1', 'create index RRL_CSL_RULE_I1 on RRL_CUSTOMER_SHELF_LIFE_RULE (CUSTOMER_ID, ARTICUL, ACTIVE, RULE_PRIORITY)');
  ensure_index('RRL_CPS_RULE_I1', 'create index RRL_CPS_RULE_I1 on RRL_CUSTOMER_PRODUCT_STACK_RULE (CUSTOMER_ID, ARTICUL, ACTIVE, RULE_PRIORITY)');
  ensure_index('RRL_CVR_I1', 'create index RRL_CVR_I1 on RRL_CUSTOMER_VEHICLE_RULE (CUSTOMER_ID, ACTIVE, RULE_PRIORITY)');
  ensure_index('RRL_SHIPMENT_PART_I1', 'create index RRL_SHIPMENT_PART_I1 on RRL_SHIPMENT_PART (CUSTOMER_ORDER_ID, STATUS)');
end;
/

merge into RRL_VEHICLE_TYPE d
using (
  select 'TRUCK_33' VEHICLE_TYPE_CODE, 'Truck 33 pallets' VEHICLE_TYPE_NAME, 33 MAX_PALLET_COUNT, null MAX_WEIGHT, null MAX_VOLUME from dual
  union all
  select 'TEN_TON', '10 ton truck', null, 10000, null from dual
  union all
  select 'SMALL_TRUCK', 'Small truck', null, null, null from dual
) s
on (d.VEHICLE_TYPE_CODE = s.VEHICLE_TYPE_CODE)
when matched then update set
  d.VEHICLE_TYPE_NAME = s.VEHICLE_TYPE_NAME,
  d.MAX_PALLET_COUNT = nvl(d.MAX_PALLET_COUNT, s.MAX_PALLET_COUNT),
  d.MAX_WEIGHT = nvl(d.MAX_WEIGHT, s.MAX_WEIGHT),
  d.MAX_VOLUME = nvl(d.MAX_VOLUME, s.MAX_VOLUME),
  d.ACTIVE = 1,
  d.UPDATED_AT = sysdate,
  d.UPDATED_BY = 'MIGRATION_015'
when not matched then insert (
  VEHICLE_TYPE_ID, VEHICLE_TYPE_CODE, VEHICLE_TYPE_NAME,
  MAX_PALLET_COUNT, MAX_WEIGHT, MAX_VOLUME, ACTIVE, CREATED_AT, CREATED_BY
) values (
  RRL_VEHICLE_TYPE_SQ.nextval, s.VEHICLE_TYPE_CODE, s.VEHICLE_TYPE_NAME,
  s.MAX_PALLET_COUNT, s.MAX_WEIGHT, s.MAX_VOLUME, 1, sysdate, 'MIGRATION_015'
);

create or replace package RRL_CUSTOMER_RULE_API as
  function resolve_vehicle_type(
    p_customer_id           number,
    p_customer_store_map_id number default null
  ) return number;

  function split_order_by_pallet_capacity(
    p_customer_order_id  number,
    p_total_pallet_count number,
    p_vehicle_type_id    number default null,
    p_created_by         varchar2 default null
  ) return number;
end RRL_CUSTOMER_RULE_API;
/

create or replace package body RRL_CUSTOMER_RULE_API as
  function resolve_vehicle_type(
    p_customer_id           number,
    p_customer_store_map_id number default null
  ) return number is
    v_vehicle_type_id number;
  begin
    begin
      select VEHICLE_TYPE_ID
        into v_vehicle_type_id
        from (
          select r.VEHICLE_TYPE_ID
            from RRL_CUSTOMER_VEHICLE_RULE r
           where r.CUSTOMER_ID = p_customer_id
             and r.ACTIVE = 1
             and (r.CUSTOMER_STORE_MAP_ID = p_customer_store_map_id or r.CUSTOMER_STORE_MAP_ID is null)
             and trunc(sysdate) between r.VALID_FROM and nvl(r.VALID_TO, date '2999-12-31')
           order by case when r.CUSTOMER_STORE_MAP_ID = p_customer_store_map_id then 0 else 1 end,
                    r.RULE_PRIORITY,
                    r.CUSTOMER_VEHICLE_RULE_ID
        )
       where rownum = 1;
      return v_vehicle_type_id;
    exception
      when no_data_found then
        null;
    end;

    begin
      select DEFAULT_VEHICLE_TYPE_ID
        into v_vehicle_type_id
        from RRL_CUSTOMER
       where CUSTOMER_ID = p_customer_id
         and DEFAULT_VEHICLE_TYPE_ID is not null;
      return v_vehicle_type_id;
    exception
      when no_data_found then
        null;
    end;

    select VEHICLE_TYPE_ID
      into v_vehicle_type_id
      from RRL_VEHICLE_TYPE
     where VEHICLE_TYPE_CODE = 'TRUCK_33';

    return v_vehicle_type_id;
  end resolve_vehicle_type;

  function split_order_by_pallet_capacity(
    p_customer_order_id  number,
    p_total_pallet_count number,
    p_vehicle_type_id    number default null,
    p_created_by         varchar2 default null
  ) return number is
    v_order RRL_CUSTOMER_ORDER%rowtype;
    v_vehicle_type_id number;
    v_max_pallet_count number;
    v_remaining number;
    v_part_no number := 0;
    v_part_count number := 0;
    v_part_pallets number;
  begin
    if p_total_pallet_count is null or p_total_pallet_count < 0 then
      raise_application_error(-20970, 'total pallet count must be greater than or equal to zero');
    end if;

    select *
      into v_order
      from RRL_CUSTOMER_ORDER
     where CUSTOMER_ORDER_ID = p_customer_order_id;

    v_vehicle_type_id := nvl(p_vehicle_type_id, resolve_vehicle_type(v_order.CUSTOMER_ID, v_order.CUSTOMER_STORE_MAP_ID));

    select nvl((
             select max(nvl(r.MAX_PALLET_COUNT, vt.MAX_PALLET_COUNT))
               from RRL_CUSTOMER_VEHICLE_RULE r
              where r.CUSTOMER_ID = v_order.CUSTOMER_ID
                and r.VEHICLE_TYPE_ID = v_vehicle_type_id
                and r.ACTIVE = 1
                and trunc(sysdate) between r.VALID_FROM and nvl(r.VALID_TO, date '2999-12-31')
           ), vt.MAX_PALLET_COUNT)
      into v_max_pallet_count
      from RRL_VEHICLE_TYPE vt
     where vt.VEHICLE_TYPE_ID = v_vehicle_type_id;

    if v_max_pallet_count is null or v_max_pallet_count <= 0 then
      v_max_pallet_count := p_total_pallet_count;
    end if;

    if v_max_pallet_count <= 0 then
      v_max_pallet_count := 1;
    end if;

    v_remaining := p_total_pallet_count;

    while v_remaining > 0 loop
      v_part_no := v_part_no + 1;
      v_part_pallets := least(v_remaining, v_max_pallet_count);

      merge into RRL_SHIPMENT_PART d
      using (
        select p_customer_order_id CUSTOMER_ORDER_ID,
               v_part_no PART_NO
          from dual
      ) s
      on (d.CUSTOMER_ORDER_ID = s.CUSTOMER_ORDER_ID and d.PART_NO = s.PART_NO)
      when matched then update set
        d.VEHICLE_TYPE_ID = v_vehicle_type_id,
        d.PLANNED_PALLET_COUNT = v_part_pallets,
        d.UPDATED_AT = sysdate,
        d.UPDATED_BY = substr(p_created_by, 1, 50)
      when not matched then insert (
        SHIPMENT_PART_ID, CUSTOMER_ORDER_ID, ROUTE_ID, DOCK_ID,
        VEHICLE_TYPE_ID, PART_NO, PLANNED_PALLET_COUNT, STATUS,
        CREATED_AT, CREATED_BY
      ) values (
        RRL_SHIPMENT_PART_SQ.nextval, p_customer_order_id, v_order.ROUTE_ID, v_order.DOCK_ID,
        v_vehicle_type_id, v_part_no, v_part_pallets, 'PLANNED',
        sysdate, substr(p_created_by, 1, 50)
      );

      v_part_count := v_part_count + 1;
      v_remaining := v_remaining - v_part_pallets;
    end loop;

    return v_part_count;
  end split_order_by_pallet_capacity;
end RRL_CUSTOMER_RULE_API;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'CUSTOMER_RULE_VIEW' RIGHT1, 'View customer picking rules' DESCR from dual
    union all
    select 'CUSTOMER_RULE_EDIT', 'Edit customer picking rules' from dual
    union all
    select 'VEHICLE_TYPE_VIEW', 'View vehicle types' from dual
    union all
    select 'VEHICLE_TYPE_EDIT', 'Edit vehicle types' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-015-customer-rules-vehicle-capacity' migration_id,
         'Customer shelf-life, stacking, vehicle capacity rules, and shipment parts' description,
         '015_apply.sql' script_name,
         '015_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-015] done
