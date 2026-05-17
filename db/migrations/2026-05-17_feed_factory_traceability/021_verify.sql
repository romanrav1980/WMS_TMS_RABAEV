prompt [migration 2026-05-17-021] Finished goods admin settings - verify

select table_name
  from user_tables
 where table_name = 'RRL_FINISHED_GOODS_SKU';

select count(*) FINISHED_GOODS_SKU_COUNT
  from RRL_FINISHED_GOODS_SKU
 where nvl(IS_FINISHED_GOODS, 0) = 1;

select count(*) FINISHED_GOODS_WAREHOUSE_COUNT
  from RRL_WARES
 where nvl(FLAG_FINISHED_GOODS, 0) = 1
    or nvl(FLAG_PRODUCTION_BUFFER, 0) = 1;

select count(*) FINISHED_GOODS_REMAIN_ROW_COUNT
  from RRL_REMAINS r
  join RRL_CELLS c on c.CELL = r.CELL
  join RRL_WARES w on w.ID = c.WARE_ID
 where nvl(w.FLAG_FINISHED_GOODS, 0) = 1
    or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1;

select count(*) FINISHED_GOODS_RIGHT_COUNT
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'FINISHED_GOODS_VIEW',
     'FINISHED_GOODS_EDIT',
     'FINISHED_GOODS_STOCK_VIEW',
     'FINISHED_GOODS_BATCH_VIEW',
     'FINISHED_GOODS_EXPORT'
   );

select count(*) INVALID_CNT
  from user_objects
 where status <> 'VALID'
   and object_type in ('PACKAGE', 'PACKAGE BODY', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW');

prompt [migration 2026-05-17-021] verify done
