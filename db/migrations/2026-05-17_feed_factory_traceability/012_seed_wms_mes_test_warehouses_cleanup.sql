prompt [seed 2026-05-17-012] WMS/MES test warehouses - cleanup

delete from RRL_REMAINS
 where UID_POLETA like 'SEED-RM-%';

delete from RRL_EVENTS
 where USER_ID = 'MESSEED'
   and UID_POLETA like 'SEED-RM-%';

delete from RRL_PALLETS
 where UID_PALLET like 'SEED-RM-%';

delete from RRL_ARTICULS
 where ACTICUL like 'RM-%';

delete from RRL_CELLS
 where WARE_ID in (9101, 9102, 9103, 9104)
   and (
     CELL like 'RM-%'
     or CELL like 'MES_%'
     or CELL like 'BUF_%'
     or CELL like 'FG-%'
   );

delete from RRL_WARES
 where ID in (9101, 9102, 9103, 9104);

commit;

prompt [seed 2026-05-17-012] cleanup done
