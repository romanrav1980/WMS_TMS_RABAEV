prompt [migration 2026-05-17-019] verify customer address vehicles and product rules

select object_name, object_type, status
  from user_objects
 where object_name in ('RRL_CUSTOMER_RULE_API')
 order by object_name, object_type;

select table_name
  from user_tables
 where table_name in ('RRL_CUSTOMER_PRODUCT_RULE')
 order by table_name;

select column_name
  from user_tab_cols
 where table_name = 'RRL_CUSTOMER_ADDRESS'
   and column_name in (
     'VEHICLE_TYPE_ID',
     'MAX_PALLET_COUNT',
     'MAX_WEIGHT',
     'MAX_VOLUME',
     'SPLIT_ORDER_BY_CAPACITY'
   )
 order by column_name;

select count(*) PRODUCT_RULE_COUNT
  from RRL_CUSTOMER_PRODUCT_RULE;

select count(*) ADDRESS_VEHICLE_COUNT
  from RRL_CUSTOMER_ADDRESS
 where VEHICLE_TYPE_ID is not null;

select count(*) INVALID_CNT
  from user_objects
 where status <> 'VALID';
