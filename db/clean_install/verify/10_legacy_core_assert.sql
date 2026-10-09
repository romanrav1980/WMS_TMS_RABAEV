set define off

prompt [verify] legacy core objects

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
      raise_application_error(-20901, 'Missing object: RABAEV.' || p_name || ' (' || p_type || ')');
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
      raise_application_error(-20902, 'Missing column: RABAEV.' || p_table || '.' || p_column);
    end if;
  end;
begin
  assert_object('RRL_TRANSPORT_TASK', 'TABLE');
  assert_object('RRL_SBORKA_PALLETS', 'TABLE');
  assert_object('RRL_SBORKA_PALLET_ROWS', 'TABLE');
  assert_object('RRL_ADDR', 'TABLE');
  assert_object('RUSERS', 'TABLE');
  assert_object('USER_GROUP', 'TABLE');
  assert_object('RIGHTS', 'TABLE');
  assert_object('RRL_CONSTANTS', 'TABLE');
  assert_object('RRL_WARES', 'TABLE');
  assert_object('RRL_VERSIONS', 'TABLE');

  assert_object('RRL_AUTH3', 'FUNCTION');
  assert_object('RRL_HAS_WRIGHT', 'FUNCTION');
  assert_object('RRL_ST_VERYFY_PERC', 'FUNCTION');
  assert_object('RRL_SUGAR_HAS', 'FUNCTION');
  assert_object('COMPL', 'PACKAGE');

  assert_column('RRL_SBORKA_PALLETS', 'CONDITION');
  assert_column('RRL_TRANSPORT_TASK', 'DELETED');
  assert_column('RRL_TR_VEHICLE', 'NUM');
  assert_column('RRL_TR_VEHICLE', 'TR_TYPE');
end;
/

prompt [verify] legacy core objects ok
