prompt [seed 2026-05-17-012] WMS/MES test warehouses - verify

select 'TEST_WARES' check_name, count(*) actual_count
  from RRL_WARES
 where ID in (9101, 9102, 9103, 9104);

select WARE_ID, count(*) cells_count
  from RRL_CELLS
 where WARE_ID in (9101, 9102, 9103, 9104)
 group by WARE_ID
 order by WARE_ID;

select 'RAW_ARTICULS' check_name, count(*) actual_count
  from RRL_ARTICULS
 where ACTICUL like 'RM-%';

select 'RAW_SEED_PALLETS' check_name, count(*) actual_count
  from RRL_PALLETS
 where UID_PALLET like 'SEED-RM-%';

select 'RAW_SEED_REMAINS' check_name,
       count(*) pallet_count,
       sum(REMAIN) total_remain
  from RRL_REMAINS
 where UID_POLETA like 'SEED-RM-%';

select c.WARE_ID,
       w.NAME ware_name,
       count(distinct r.UID_POLETA) pallet_count,
       sum(r.REMAIN) total_remain
  from RRL_REMAINS r
  join RRL_CELLS c on c.CELL = r.CELL
  left join RRL_WARES w on w.ID = c.WARE_ID
 where r.UID_POLETA like 'SEED-RM-%'
 group by c.WARE_ID, w.NAME
 order by c.WARE_ID;
