prompt [migration 2026-05-17-020] Raw material admin settings - verify

select table_name
  from user_tables
 where table_name = 'RRL_RAW_MATERIAL_SKU';

select count(*) RAW_SKU_COUNT
  from RRL_RAW_MATERIAL_SKU
 where nvl(IS_RAW_MATERIAL, 0) = 1;

select count(*) RAW_WAREHOUSE_COUNT
  from RRL_WARES
 where nvl(FLAG_RAW_MATERIAL, 0) = 1;

select count(*) RAW_REMAIN_ROW_COUNT
  from RRL_REMAINS r
  join RRL_CELLS c on c.CELL = r.CELL
  join RRL_WARES w on w.ID = c.WARE_ID
 where nvl(w.FLAG_RAW_MATERIAL, 0) = 1;

select count(*) RAW_RIGHT_COUNT
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'RAW_MATERIAL_VIEW',
     'RAW_MATERIAL_EDIT',
     'RAW_MATERIAL_STOCK_VIEW',
     'RAW_MATERIAL_EXPORT'
   );

select count(*) INVALID_CNT
  from user_objects
 where status <> 'VALID'
   and object_type in ('PACKAGE', 'PACKAGE BODY', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW');

prompt [migration 2026-05-17-020] verify done
