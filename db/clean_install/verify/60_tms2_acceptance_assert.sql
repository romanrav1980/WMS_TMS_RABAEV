set define off

prompt [verify] TMS-2 acceptance fixtures

declare
  v_count number;
  procedure assert_positive(p_value number, p_name varchar2) is
  begin
    if p_value <= 0 then
      raise_application_error(-20951, 'Expected acceptance fixture rows: ' || p_name);
    end if;
  end;

begin
  select count(*) into v_count from RABAEV.RRL_WARES where ID in (9201, 9202, 9203);
  assert_positive(v_count, 'Dobrotseny warehouses');

  select count(*) into v_count from RABAEV.RRL_SBORKA_PALLETS where STDATE = date '2026-05-24';
  assert_positive(v_count, 'Dobrotseny ST rows for 2026-05-24');

  select count(*) into v_count from RABAEV.RRL_PLANNER_PLANS where SOLVER = 's9-template-fixture';
  assert_positive(v_count, 'Sprint 9 planner template fixture');

  select count(*) into v_count from RABAEV.RRL_ADDR_TEST_GEOCODE_BAK where MIGRATION_TAG = '063_tms2_test_geocode';
  assert_positive(v_count, 'test geocode backup rows');
end;
/

prompt [verify] TMS-2 acceptance fixtures ok
