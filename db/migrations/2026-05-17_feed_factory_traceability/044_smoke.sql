prompt [migration 2026-05-23-044] ban zero warehouse id - smoke

declare
  v_failed number := 0;
begin
  begin
    insert into RRL_WARES (ID, NAME, PREFIX)
    values (0, 'ZERO SHOULD FAIL', 'Z0');
    v_failed := 1;
  exception
    when others then
      if sqlcode != -2290 then
        raise;
      end if;
  end;

  if v_failed = 1 then
    raise_application_error(-20044, 'RRL_WARES accepted ID=0');
  end if;

  begin
    insert into RRL_WAREHOUSE_MAP_CANVAS (
      CANVAS_ID, WARE_ID, CANVAS_CODE, CANVAS_NAME, VERSION_NO, STATUS,
      RENDERER_KIND, UNIT_CODE, GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS
    ) values (
      RRL_WH_MAP_CANVAS_SQ.nextval, 0, 'SMOKE-ZERO-CANVAS', 'Smoke zero canvas', 1, 'DRAFT',
      'CANVAS_2D', 'METER', 1.2, 0.8, 1
    );
    v_failed := 1;
  exception
    when others then
      if sqlcode != -2290 then
        raise;
      end if;
  end;

  if v_failed = 1 then
    raise_application_error(-20045, 'RRL_WAREHOUSE_MAP_CANVAS accepted WARE_ID=0');
  end if;
end;
/

prompt [migration 2026-05-23-044] smoke done
