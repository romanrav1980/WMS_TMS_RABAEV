prompt [migration 2026-05-22-041] warehouse map canvas and cell slots - smoke cleanup

delete from RRL_PICK_ROUTE_CELL
 where CELL_SLOT_ID in (
   select CELL_SLOT_ID from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041'
 );
delete from RRL_STOCK_RESERVATION
 where CELL_SLOT_ID in (
   select CELL_SLOT_ID from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041'
 );
delete from RRL_WAREHOUSE_TASK
 where FROM_CELL_SLOT_ID in (
   select CELL_SLOT_ID from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041'
 )
    or TO_CELL_SLOT_ID in (
   select CELL_SLOT_ID from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041'
 );
delete from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041';
delete from RRL_TOPOLOGY_CELL where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_PASSAGE where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_OBJECT where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_041';

commit;

select 'SMOKE_041_LEFTOVERS' check_name,
       (
         select count(*) from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041'
       ) +
       (
         select count(*) from RRL_TOPOLOGY_CELL where CREATED_BY = 'SMOKE_041'
       ) +
       (
         select count(*) from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_041'
       ) +
       (
         select count(*) from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_041'
       ) +
       (
         select count(*) from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = 'SMOKE_041'
       ) +
       (
         select count(*) from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = 'SMOKE_041'
       ) leftovers
  from dual;

prompt [migration 2026-05-22-041] smoke cleanup done
