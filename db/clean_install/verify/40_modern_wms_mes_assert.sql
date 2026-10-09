set define off

prompt [verify] modern WMS/MES/traceability/warehouse-map objects

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
      raise_application_error(-20931, 'Missing modern object: RABAEV.' || p_name || ' (' || p_type || ')');
    end if;
  end;
begin
  assert_object('RRL_SCHEMA_MIGRATIONS', 'TABLE');
  assert_object('RRL_API_CALL_LOG', 'TABLE');
  assert_object('RRL_SQL_SLOW_LOG', 'TABLE');
  assert_object('RRL_REGULATORY_OUTBOX', 'TABLE');
  assert_object('RRL_WAREHOUSE_TASK_SYNC', 'TABLE');
  assert_object('RRL_TOPOLOGY_CELL', 'TABLE');
  assert_object('RRL_WAREHOUSE_MAP_CANVAS', 'TABLE');
end;
/

prompt [verify] modern WMS/MES/traceability/warehouse-map objects ok
