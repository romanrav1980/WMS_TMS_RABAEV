-- 2026-05-17-009-bom-production-block smoke cleanup

delete from RRL_TRACE_EVENT
 where ENTITY_TYPE = 'BOM'
   and ENTITY_ID in (
     select to_char(BOM_ID)
       from RRL_BOM
      where BOM_CODE like 'SMOKE-009%'
   );

delete from RRL_BOM_AUDIT
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE like 'SMOKE-009%'
 );

delete from RRL_BOM_LINE
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE like 'SMOKE-009%'
 );

delete from RRL_BOM
 where BOM_CODE like 'SMOKE-009%';

commit;

select 'SMOKE_009_BOM_ROWS' check_name,
       count(*) rows_found
  from RRL_BOM
 where BOM_CODE like 'SMOKE-009%';
