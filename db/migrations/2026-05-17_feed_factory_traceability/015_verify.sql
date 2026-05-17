prompt [migration 2026-05-17-015] verify

select table_name
  from user_tables
 where table_name in (
   'RRL_CUSTOMER_SHELF_LIFE_RULE',
   'RRL_CUSTOMER_PRODUCT_STACK_RULE',
   'RRL_VEHICLE_TYPE',
   'RRL_CUSTOMER_VEHICLE_RULE',
   'RRL_SHIPMENT_PART'
 )
 order by table_name;

select vehicle_type_code, vehicle_type_name, max_pallet_count, active
  from RRL_VEHICLE_TYPE
 order by vehicle_type_code;

select object_type, object_name, status
  from user_objects
 where object_name = 'RRL_CUSTOMER_RULE_API'
 order by object_type, object_name;

select right1, user_group
  from rights
 where user_group = 'GLOBAL_ADMIN'
   and upper(right1) in (
     'CUSTOMER_RULE_VIEW',
     'CUSTOMER_RULE_EDIT',
     'VEHICLE_TYPE_VIEW',
     'VEHICLE_TYPE_EDIT'
   )
 order by right1;

prompt [migration 2026-05-17-015] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
