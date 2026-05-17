prompt [migration 2026-05-17-014] verify

select table_name
  from user_tables
 where table_name in (
   'RRL_CUSTOMER',
   'RRL_CUSTOMER_ADDRESS',
   'RRL_CUSTOMER_STORE_MAP',
   'RRL_CUSTOMER_ORDER',
   'RRL_CUSTOMER_ORDER_ROW',
   'RRL_CUSTOMER_ORDER_FULFILLMENT'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_CUSTOMER_SQ',
   'RRL_CUSTOMER_ADDRESS_SQ',
   'RRL_CUSTOMER_STORE_MAP_SQ',
   'RRL_CUSTOMER_ORDER_SQ',
   'RRL_CUSTOMER_ORDER_ROW_SQ',
   'RRL_CUSTOMER_ORDER_FULF_SQ'
 )
 order by sequence_name;

select object_type, object_name, status
  from user_objects
 where object_name = 'RRL_CUSTOMER_ORDER_API'
 order by object_type, object_name;

select right1, user_group
  from rights
 where user_group = 'GLOBAL_ADMIN'
   and upper(right1) in (
     'CUSTOMER_VIEW',
     'CUSTOMER_EDIT',
     'CUSTOMER_ORDER_VIEW',
     'CUSTOMER_ORDER_IMPORT',
     'CUSTOMER_FULFILLMENT_VIEW'
   )
 order by right1;

prompt [migration 2026-05-17-014] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
