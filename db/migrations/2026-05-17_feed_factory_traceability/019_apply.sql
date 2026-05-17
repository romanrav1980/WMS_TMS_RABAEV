prompt [migration 2026-05-17-019] Customer address vehicles and unified product rules - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_cols
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

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

  procedure ensure_fk(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_constraints where constraint_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_column('RRL_CUSTOMER_ADDRESS', 'VEHICLE_TYPE_ID',
    'alter table RRL_CUSTOMER_ADDRESS add VEHICLE_TYPE_ID number');
  ensure_column('RRL_CUSTOMER_ADDRESS', 'MAX_PALLET_COUNT',
    'alter table RRL_CUSTOMER_ADDRESS add MAX_PALLET_COUNT number');
  ensure_column('RRL_CUSTOMER_ADDRESS', 'MAX_WEIGHT',
    'alter table RRL_CUSTOMER_ADDRESS add MAX_WEIGHT number');
  ensure_column('RRL_CUSTOMER_ADDRESS', 'MAX_VOLUME',
    'alter table RRL_CUSTOMER_ADDRESS add MAX_VOLUME number');
  ensure_column('RRL_CUSTOMER_ADDRESS', 'SPLIT_ORDER_BY_CAPACITY',
    'alter table RRL_CUSTOMER_ADDRESS add SPLIT_ORDER_BY_CAPACITY number(1) default 1 not null');

  ensure_fk('RRL_CUSTOMER_ADDRESS_FK2',
    'alter table RRL_CUSTOMER_ADDRESS add constraint RRL_CUSTOMER_ADDRESS_FK2 foreign key (VEHICLE_TYPE_ID) references RRL_VEHICLE_TYPE (VEHICLE_TYPE_ID)');
  ensure_fk('RRL_CUSTOMER_ADDRESS_CHK3',
    'alter table RRL_CUSTOMER_ADDRESS add constraint RRL_CUSTOMER_ADDRESS_CHK3 check (SPLIT_ORDER_BY_CAPACITY in (0, 1))');

  ensure_table('RRL_CUSTOMER_PRODUCT_RULE', q'[
    create table RRL_CUSTOMER_PRODUCT_RULE (
      CUSTOMER_PRODUCT_RULE_ID number not null,
      CUSTOMER_ID number not null,
      CUSTOMER_STORE_MAP_ID number,
      ARTICUL varchar2(40),
      PRODUCT_GROUP varchar2(100),
      MIN_SHELF_LIFE_DAYS number,
      MIN_SHELF_LIFE_PERCENT number,
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
      constraint RRL_CUSTOMER_PRODUCT_RULE_PK primary key (CUSTOMER_PRODUCT_RULE_ID),
      constraint RRL_CUSTOMER_PRODUCT_RULE_FK1 foreign key (CUSTOMER_ID) references RRL_CUSTOMER (CUSTOMER_ID),
      constraint RRL_CUSTOMER_PRODUCT_RULE_FK2 foreign key (CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP (CUSTOMER_STORE_MAP_ID),
      constraint RRL_CUSTOMER_PRODUCT_RULE_CHK1 check (ACTIVE in (0, 1)),
      constraint RRL_CUSTOMER_PRODUCT_RULE_CHK2 check (ALLOW_TOP_STACKING in (0, 1)),
      constraint RRL_CUSTOMER_PRODUCT_RULE_CHK3 check (MUST_BE_SEPARATE_PALLET in (0, 1)),
      constraint RRL_CUSTOMER_PRODUCT_RULE_CHK4 check (MIN_SHELF_LIFE_PERCENT is null or (MIN_SHELF_LIFE_PERCENT >= 0 and MIN_SHELF_LIFE_PERCENT <= 100)),
      constraint RRL_CUSTOMER_PRODUCT_RULE_CHK5 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_sequence('RRL_CUSTOMER_PRODUCT_RULE_SQ',
    'create sequence RRL_CUSTOMER_PRODUCT_RULE_SQ start with 1 increment by 1 nocache');
  ensure_index('RRL_CUSTOMER_PRODUCT_RULE_I1',
    'create index RRL_CUSTOMER_PRODUCT_RULE_I1 on RRL_CUSTOMER_PRODUCT_RULE (CUSTOMER_ID, ARTICUL, ACTIVE, RULE_PRIORITY)');
  ensure_index('RRL_CUSTOMER_ADDRESS_I2',
    'create index RRL_CUSTOMER_ADDRESS_I2 on RRL_CUSTOMER_ADDRESS (CUSTOMER_ID, VEHICLE_TYPE_ID, ACTIVE)');
end;
/

insert into RRL_CUSTOMER_PRODUCT_RULE (
  CUSTOMER_PRODUCT_RULE_ID, CUSTOMER_ID, CUSTOMER_STORE_MAP_ID,
  ARTICUL, PRODUCT_GROUP, MIN_SHELF_LIFE_DAYS, MIN_SHELF_LIFE_PERCENT,
  PALLET_CASE_QTY, PALLET_LAYER_QTY, PALLET_LAYER_COUNT,
  MAX_PALLET_WEIGHT, MAX_PALLET_VOLUME, MAX_PALLET_HEIGHT,
  PALLET_TYPE, ALLOW_TOP_STACKING, MUST_BE_SEPARATE_PALLET,
  STACK_COMPATIBILITY_GROUP, RULE_PRIORITY, ACTIVE, VALID_FROM, VALID_TO,
  CREATED_AT, CREATED_BY
)
select RRL_CUSTOMER_PRODUCT_RULE_SQ.nextval,
       g.CUSTOMER_ID,
       g.CUSTOMER_STORE_MAP_ID,
       g.ARTICUL,
       g.PRODUCT_GROUP,
       g.MIN_SHELF_LIFE_DAYS,
       g.MIN_SHELF_LIFE_PERCENT,
       g.PALLET_CASE_QTY,
       g.PALLET_LAYER_QTY,
       g.PALLET_LAYER_COUNT,
       g.MAX_PALLET_WEIGHT,
       g.MAX_PALLET_VOLUME,
       g.MAX_PALLET_HEIGHT,
       g.PALLET_TYPE,
       g.ALLOW_TOP_STACKING,
       g.MUST_BE_SEPARATE_PALLET,
       g.STACK_COMPATIBILITY_GROUP,
       g.RULE_PRIORITY,
       g.ACTIVE,
       g.VALID_FROM,
       g.VALID_TO,
       sysdate,
       'MIGRATION_019'
  from (
    select x.CUSTOMER_ID,
           x.CUSTOMER_STORE_MAP_ID,
           x.ARTICUL,
           x.PRODUCT_GROUP,
           max(x.MIN_SHELF_LIFE_DAYS) MIN_SHELF_LIFE_DAYS,
           max(x.MIN_SHELF_LIFE_PERCENT) MIN_SHELF_LIFE_PERCENT,
           max(x.PALLET_CASE_QTY) PALLET_CASE_QTY,
           max(x.PALLET_LAYER_QTY) PALLET_LAYER_QTY,
           max(x.PALLET_LAYER_COUNT) PALLET_LAYER_COUNT,
           max(x.MAX_PALLET_WEIGHT) MAX_PALLET_WEIGHT,
           max(x.MAX_PALLET_VOLUME) MAX_PALLET_VOLUME,
           max(x.MAX_PALLET_HEIGHT) MAX_PALLET_HEIGHT,
           max(x.PALLET_TYPE) PALLET_TYPE,
           max(x.ALLOW_TOP_STACKING) ALLOW_TOP_STACKING,
           max(x.MUST_BE_SEPARATE_PALLET) MUST_BE_SEPARATE_PALLET,
           max(x.STACK_COMPATIBILITY_GROUP) STACK_COMPATIBILITY_GROUP,
           min(x.RULE_PRIORITY) RULE_PRIORITY,
           max(x.ACTIVE) ACTIVE,
           min(x.VALID_FROM) VALID_FROM,
           max(x.VALID_TO) VALID_TO
      from (
        select CUSTOMER_ID, CUSTOMER_STORE_MAP_ID, ARTICUL, PRODUCT_GROUP,
               MIN_SHELF_LIFE_DAYS, MIN_SHELF_LIFE_PERCENT,
               null PALLET_CASE_QTY, null PALLET_LAYER_QTY, null PALLET_LAYER_COUNT,
               null MAX_PALLET_WEIGHT, null MAX_PALLET_VOLUME, null MAX_PALLET_HEIGHT,
               null PALLET_TYPE, 0 ALLOW_TOP_STACKING, 0 MUST_BE_SEPARATE_PALLET,
               null STACK_COMPATIBILITY_GROUP, RULE_PRIORITY, ACTIVE, VALID_FROM, VALID_TO
          from RRL_CUSTOMER_SHELF_LIFE_RULE
        union all
        select CUSTOMER_ID, CUSTOMER_STORE_MAP_ID, ARTICUL, PRODUCT_GROUP,
               null MIN_SHELF_LIFE_DAYS, null MIN_SHELF_LIFE_PERCENT,
               PALLET_CASE_QTY, PALLET_LAYER_QTY, PALLET_LAYER_COUNT,
               MAX_PALLET_WEIGHT, MAX_PALLET_VOLUME, MAX_PALLET_HEIGHT,
               PALLET_TYPE, ALLOW_TOP_STACKING, MUST_BE_SEPARATE_PALLET,
               STACK_COMPATIBILITY_GROUP, RULE_PRIORITY, ACTIVE, VALID_FROM, VALID_TO
          from RRL_CUSTOMER_PRODUCT_STACK_RULE
       ) x
 where not exists (
       select 1
         from RRL_CUSTOMER_PRODUCT_RULE r
        where r.CUSTOMER_ID = x.CUSTOMER_ID
          and nvl(r.CUSTOMER_STORE_MAP_ID, -1) = nvl(x.CUSTOMER_STORE_MAP_ID, -1)
          and nvl(r.ARTICUL, chr(1)) = nvl(x.ARTICUL, chr(1))
          and nvl(r.PRODUCT_GROUP, chr(1)) = nvl(x.PRODUCT_GROUP, chr(1))
      )
 group by x.CUSTOMER_ID, x.CUSTOMER_STORE_MAP_ID, x.ARTICUL, x.PRODUCT_GROUP
       ) g;

merge into RRL_CUSTOMER_ADDRESS a
using (
  select CUSTOMER_ADDRESS_ID,
         VEHICLE_TYPE_ID,
         MAX_PALLET_COUNT,
         MAX_WEIGHT,
         MAX_VOLUME,
         SPLIT_ORDER_BY_CAPACITY
    from (
      select a.CUSTOMER_ADDRESS_ID,
             r.VEHICLE_TYPE_ID,
             r.MAX_PALLET_COUNT,
             r.MAX_WEIGHT,
             r.MAX_VOLUME,
             r.SPLIT_ORDER_BY_CAPACITY,
             row_number() over (
               partition by a.CUSTOMER_ADDRESS_ID
               order by r.RULE_PRIORITY, r.CUSTOMER_VEHICLE_RULE_ID
             ) rn
        from RRL_CUSTOMER_ADDRESS a
        join RRL_CUSTOMER_VEHICLE_RULE r
          on r.CUSTOMER_ID = a.CUSTOMER_ID
         and r.ACTIVE = 1
       where a.ADDRESS_TYPE in ('DELIVERY', 'STORE')
         and a.VEHICLE_TYPE_ID is null
    )
   where rn = 1
) s
on (a.CUSTOMER_ADDRESS_ID = s.CUSTOMER_ADDRESS_ID)
when matched then update set
  a.VEHICLE_TYPE_ID = s.VEHICLE_TYPE_ID,
  a.MAX_PALLET_COUNT = s.MAX_PALLET_COUNT,
  a.MAX_WEIGHT = s.MAX_WEIGHT,
  a.MAX_VOLUME = s.MAX_VOLUME,
  a.SPLIT_ORDER_BY_CAPACITY = nvl(s.SPLIT_ORDER_BY_CAPACITY, 1),
  a.UPDATED_AT = sysdate,
  a.UPDATED_BY = 'MIGRATION_019';

update RRL_CUSTOMER_ADDRESS a
   set a.VEHICLE_TYPE_ID = (
         select c.DEFAULT_VEHICLE_TYPE_ID
           from RRL_CUSTOMER c
          where c.CUSTOMER_ID = a.CUSTOMER_ID
            and c.DEFAULT_VEHICLE_TYPE_ID is not null
       ),
       a.UPDATED_AT = sysdate,
       a.UPDATED_BY = 'MIGRATION_019'
 where a.VEHICLE_TYPE_ID is null
   and exists (
       select 1
         from RRL_CUSTOMER c
        where c.CUSTOMER_ID = a.CUSTOMER_ID
          and c.DEFAULT_VEHICLE_TYPE_ID is not null
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
          select a.VEHICLE_TYPE_ID
            from RRL_CUSTOMER_ADDRESS a
           where a.CUSTOMER_ID = p_customer_id
             and a.ACTIVE = 1
             and a.VEHICLE_TYPE_ID is not null
             and a.ADDRESS_TYPE in ('DELIVERY', 'STORE')
           order by case when a.ADDRESS_TYPE = 'DELIVERY' then 0 else 1 end,
                    a.CUSTOMER_ADDRESS_ID
        )
       where rownum = 1;
      return v_vehicle_type_id;
    exception
      when no_data_found then
        null;
    end;

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
             select max(nvl(a.MAX_PALLET_COUNT, vt.MAX_PALLET_COUNT))
               from RRL_CUSTOMER_ADDRESS a
              where a.CUSTOMER_ID = v_order.CUSTOMER_ID
                and a.VEHICLE_TYPE_ID = v_vehicle_type_id
                and a.ACTIVE = 1
           ), nvl((
             select max(nvl(r.MAX_PALLET_COUNT, vt.MAX_PALLET_COUNT))
               from RRL_CUSTOMER_VEHICLE_RULE r
              where r.CUSTOMER_ID = v_order.CUSTOMER_ID
                and r.VEHICLE_TYPE_ID = v_vehicle_type_id
                and r.ACTIVE = 1
                and trunc(sysdate) between r.VALID_FROM and nvl(r.VALID_TO, date '2999-12-31')
           ), vt.MAX_PALLET_COUNT))
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

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-019-customer-address-vehicles-product-rules' migration_id,
         'Move customer vehicle parameters to addresses and add unified product rules' description,
         '019_apply.sql' script_name,
         '019_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-019] done
