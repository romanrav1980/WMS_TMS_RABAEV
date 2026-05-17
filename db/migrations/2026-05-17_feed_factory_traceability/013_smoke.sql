prompt [migration 2026-05-17-013] smoke

merge into RRL_ARTICULS d
using (
  select 'FG-AGING-SMOKE-013' ACTICUL,
         1 NORMA_UKLADKI,
         'MES aging smoke product' NAME,
         'KG' UNIT_TYPE,
         'SMOKE013' BARCODE_SHT,
         24 SHIPMENT_AGING_HOURS
    from dual
) s
on (d.ACTICUL = s.ACTICUL)
when matched then update set
  d.SHIPMENT_AGING_HOURS = s.SHIPMENT_AGING_HOURS,
  d.SHIPMENT_AGING_COMMENT = 'Smoke aging norm: 24 hours'
when not matched then insert (
  ACTICUL, NORMA_UKLADKI, NAME, UNIT_TYPE, BARCODE_SHT,
  SHIPMENT_AGING_HOURS, SHIPMENT_AGING_COMMENT
) values (
  s.ACTICUL, s.NORMA_UKLADKI, s.NAME, s.UNIT_TYPE, s.BARCODE_SHT,
  s.SHIPMENT_AGING_HOURS, 'Smoke aging norm: 24 hours'
);

declare
  v_batch_id number;
begin
  v_batch_id := RRL_PRODUCTION_API.create_prod_batch(
    p_prod_batch_no => 'SMOKE-BATCH-013-AGING',
    p_articul => 'FG-AGING-SMOKE-013',
    p_total_quantity => 10,
    p_unit_code => 'KG',
    p_source_system => 'SMOKE-013',
    p_source_message_id => 'SMOKE-013-AGING',
    p_produced_date_from => sysdate,
    p_produced_date_to => sysdate,
    p_created_by => 'smoke-013'
  );

  update RRL_PROD_BATCH
     set QUALITY_STATUS = 'RELEASED',
         UPDATED_AT = sysdate,
         UPDATED_BY = 'smoke-013'
   where PROD_BATCH_ID = v_batch_id;
end;
/

select PROD_BATCH_NO,
       QUALITY_STATUS,
       AGING_REQUIRED_HOURS,
       round((SHIPMENT_ALLOWED_AT - CREATED_AT) * 24) APPROX_AGING_HOURS,
       SHIPMENT_EFFECTIVE_STATUS,
       IS_SHIPMENT_ALLOWED
  from RRL_PROD_BATCH_READY_V
 where PROD_BATCH_NO = 'SMOKE-BATCH-013-AGING';

declare
  v_bad number;
begin
  select count(*)
    into v_bad
    from RRL_PROD_BATCH_READY_V
   where PROD_BATCH_NO = 'SMOKE-BATCH-013-AGING'
     and QUALITY_STATUS = 'RELEASED'
     and AGING_REQUIRED_HOURS = 24
     and SHIPMENT_EFFECTIVE_STATUS = 'WAIT_AGING'
     and IS_SHIPMENT_ALLOWED = 0;

  if v_bad <> 1 then
    raise_application_error(-20013, '013 aging smoke failed.');
  end if;
end;
/

commit;

prompt [migration 2026-05-17-013] smoke done
