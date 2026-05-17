-- 2026-05-17-009-bom-production-block smoke

declare
  v_bom_id number;
  v_line_id number;
  v_found_bom_id number;
begin
  v_bom_id := RRL_BOM_API.create_bom(
    p_bom_code => 'SMOKE-009-BOM',
    p_bom_name => 'Smoke BOM 009',
    p_target_articul => 'SMOKE-FG-009',
    p_bom_kind => 'FINISHED_GOODS',
    p_base_qty => 1000,
    p_base_unit_code => 'KG',
    p_is_primary => 1,
    p_valid_from => date '2026-01-01',
    p_valid_to => date '2026-12-31',
    p_comment_text => 'Migration 009 smoke test',
    p_created_by => 'SMOKE'
  );

  v_line_id := RRL_BOM_API.add_line(
    p_bom_id => v_bom_id,
    p_line_no => 10,
    p_component_type => 'RAW',
    p_component_articul => 'RAW-009',
    p_component_name => 'Smoke raw material',
    p_qty_per_base => 600,
    p_unit_code => 'KG',
    p_loss_percent => 2,
    p_created_by => 'SMOKE'
  );

  RRL_BOM_API.approve_bom(
    p_bom_id => v_bom_id,
    p_approved_by => 'SMOKE'
  );

  v_found_bom_id := RRL_BOM_API.find_primary_bom(
    p_target_articul => 'SMOKE-FG-009',
    p_planned_date => date '2026-05-17'
  );

  if v_found_bom_id <> v_bom_id then
    raise_application_error(-20120, 'Smoke primary BOM search returned unexpected result.');
  end if;
end;
/

select BOM_ID, BOM_CODE, TARGET_ARTICUL, STATUS, IS_PRIMARY, BASE_QTY, BASE_UNIT_CODE
  from RRL_BOM
 where BOM_CODE = 'SMOKE-009-BOM';

select BOM_LINE_ID, BOM_ID, LINE_NO, COMPONENT_TYPE, COMPONENT_ARTICUL, QTY_PER_BASE, UNIT_CODE, LOSS_PERCENT
  from RRL_BOM_LINE
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE = 'SMOKE-009-BOM'
 );

select ACTION_TYPE, OLD_STATUS, NEW_STATUS, CREATED_BY
  from RRL_BOM_AUDIT
 where BOM_ID in (
   select BOM_ID
     from RRL_BOM
    where BOM_CODE = 'SMOKE-009-BOM'
 )
 order by BOM_AUDIT_ID;
