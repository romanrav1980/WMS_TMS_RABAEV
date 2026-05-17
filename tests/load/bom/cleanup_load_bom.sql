-- Cleanup for BOM load tests.
-- Safe scope: removes only rows whose BOM_CODE starts with LOAD-BOM-.

delete from RRL_TRACE_EVENT
 where ENTITY_TYPE = 'BOM'
   and ENTITY_ID in (
     select to_char(BOM_ID)
       from RRL_BOM
      where BOM_CODE like 'LOAD-BOM-%'
   );

delete from RRL_BOM_AUDIT
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE like 'LOAD-BOM-%'
 );

delete from RRL_BOM_LINE
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE like 'LOAD-BOM-%'
 );

delete from RRL_BOM
 where BOM_CODE like 'LOAD-BOM-%';

commit;

select 'RRL_BOM' table_name, count(*) rows_found
  from RRL_BOM
 where BOM_CODE like 'LOAD-BOM-%'
union all
select 'RRL_BOM_LINE', count(*)
  from RRL_BOM_LINE
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'LOAD-BOM-%')
union all
select 'RRL_BOM_AUDIT', count(*)
  from RRL_BOM_AUDIT
 where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'LOAD-BOM-%');
