package body RRL_CUSTOMER_ORDER_API as
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
