prompt [migration 2026-05-17-013] verify

select table_name, column_name, data_type, data_length
  from user_tab_columns
 where (table_name = 'RRL_ARTICULS' and column_name in ('SHIPMENT_AGING_HOURS', 'SHIPMENT_AGING_COMMENT'))
    or (table_name = 'RRL_PROD_BATCH' and column_name in (
      'AGING_REQUIRED_HOURS',
      'AGING_UNTIL',
      'SHIPMENT_ALLOWED_AT',
      'SHIPMENT_RELEASE_STATUS',
      'SHIPMENT_BLOCK_REASON'
    ))
 order by table_name, column_name;

select object_type, object_name, status
  from user_objects
 where object_name in ('RRL_TRG_PROD_BATCH_SHIP_READY', 'RRL_PROD_BATCH_READY_V')
 order by object_type, object_name;

select right1, user_group
  from rights
 where user_group = 'GLOBAL_ADMIN'
   and upper(right1) in ('QUALITY_BATCH_VIEW', 'QUALITY_BATCH_EDIT')
 order by right1;

prompt [migration 2026-05-17-013] invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
