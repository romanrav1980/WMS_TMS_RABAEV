set define off

prompt [verify] TMS-2 production objects

declare
  procedure assert_object(p_name varchar2, p_type varchar2) is
    v_count number;
  begin
    select count(*)
      into v_count
      from all_objects
     where owner = 'RABAEV'
       and object_name = upper(p_name)
       and object_type = upper(p_type);

    if v_count = 0 then
      raise_application_error(-20941, 'Missing TMS-2 object: RABAEV.' || p_name || ' (' || p_type || ')');
    end if;
  end;

  procedure assert_column(p_table varchar2, p_column varchar2) is
    v_count number;
  begin
    select count(*)
      into v_count
      from all_tab_columns
     where owner = 'RABAEV'
       and table_name = upper(p_table)
       and column_name = upper(p_column);

    if v_count = 0 then
      raise_application_error(-20942, 'Missing TMS-2 column: RABAEV.' || p_table || '.' || p_column);
    end if;
  end;
begin
  assert_object('RRL_V_AVAILABLE_STS', 'VIEW');
  assert_object('RRL_ADDR_DISTANCE_MATRIX', 'TABLE');
  assert_object('RRL_PLANNER_PLANS', 'TABLE');
  assert_object('RRL_TRANSPORT_NORMS', 'TABLE');
  assert_object('RRL_TT_OPERATIONS', 'TABLE');
  assert_object('RRL_BILL_ORDERS', 'TABLE');
  assert_object('RRL_PUSH_SUBSCRIPTIONS', 'TABLE');
  assert_object('RRL_NOTIFICATION_SETTINGS', 'TABLE');
  assert_object('RRL_VEHICLE_GPS', 'TABLE');
  assert_object('RRL_VEHICLE_GPS_LAST', 'TABLE');
  assert_object('RRL_TR_VEHICLE_ADD', 'FUNCTION');
  assert_object('RRL_TR_VEHICLE_UPDATE', 'PROCEDURE');
  assert_object('RRL_TR_VODITEL_ADD', 'FUNCTION');

  assert_column('RRL_ADDR', 'MAX_VEHICLE_TONS');
  assert_column('RRL_ADDR', 'UNLOAD_NORM_MIN');
  assert_column('RRL_ADDR', 'TW_STRICT');
  assert_column('RRL_ADDR', 'GEO_FENCE_RADIUS_M');
  assert_column('RRL_TR_VEHICLE', 'MAX_WEIGHT_KG');
  assert_column('RRL_TR_VEHICLE', 'SOBSTVENNYY');
  assert_column('RRL_TR_VODITEL', 'LICENSE_NUMBER');
  assert_column('RRL_TR_VODITEL', 'COMPANY');
end;
/

prompt [verify] TMS-2 production objects ok
