set define off

prompt [verify] legacy master data

declare
  v_count number;
  procedure assert_positive(p_value number, p_name varchar2) is
  begin
    if p_value <= 0 then
      raise_application_error(-20921, 'Expected master data rows: ' || p_name);
    end if;
  end;

begin
  select count(*) into v_count from RABAEV.RRL_ADDR;
  assert_positive(v_count, 'RRL_ADDR');

  select count(*) into v_count from RABAEV.RRL_ARTICULS;
  assert_positive(v_count, 'RRL_ARTICULS');

  select count(*) into v_count from RABAEV.RRL_CELLS;
  assert_positive(v_count, 'RRL_CELLS');

  select count(*) into v_count from RABAEV.RRL_TR_VEHICLE;
  assert_positive(v_count, 'RRL_TR_VEHICLE');

  select count(*) into v_count from RABAEV.RRL_TR_VODITEL;
  assert_positive(v_count, 'RRL_TR_VODITEL');
end;
/

prompt [verify] legacy master data ok
