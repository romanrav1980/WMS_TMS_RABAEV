set define off
select object_type, status, count(*) cnt
  from dba_objects
 where owner = 'RABAEV'
 group by object_type, status
 order by object_type, status;

select 'RRL_ARTICULS' table_name, count(*) cnt from RABAEV.RRL_ARTICULS
union all select 'RRL_CELLS', count(*) from RABAEV.RRL_CELLS
union all select 'RUSERS', count(*) from RABAEV.RUSERS
union all select 'RRL_TRANSPORT_TASK', count(*) from RABAEV.RRL_TRANSPORT_TASK
union all select 'RRL_SBORKA_PALLETS', count(*) from RABAEV.RRL_SBORKA_PALLETS
union all select 'RRL_SBORKA_PALLET_ROWS', count(*) from RABAEV.RRL_SBORKA_PALLET_ROWS;