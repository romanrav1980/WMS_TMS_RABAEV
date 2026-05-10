prompt Repair sequences after flashback of pre-DDL table data
declare
  sfera_max_id number;

  procedure move_sequence_after(seq_name varchar2, target_value number, normal_increment number default 1) is
    current_value number;
    delta number;
  begin
    execute immediate 'select RABAEV.' || seq_name || '.nextval from dual' into current_value;

    if current_value < target_value then
      delta := target_value - current_value;
      execute immediate 'alter sequence RABAEV.' || seq_name || ' increment by ' || delta;
      execute immediate 'select RABAEV.' || seq_name || '.nextval from dual' into current_value;
      execute immediate 'alter sequence RABAEV.' || seq_name || ' increment by ' || normal_increment;
    end if;
  end;

  function scalar_number(sql_text varchar2) return number is
    value number;
  begin
    execute immediate sql_text into value;
    return value;
  end;

begin
  move_sequence_after('MODS_SEQ', scalar_number('select nvl(max(ID), 0) + 1 from RABAEV.RRL_ARTICUL_MODS'));
  move_sequence_after('RRL_SBORKA_PALLET_ROWS_SQ', scalar_number('select nvl(max(ID), 0) + 1 from RABAEV.RRL_SBORKA_PALLET_ROWS'));
  move_sequence_after('RRL_TRANSPORT_TASK_SQ', scalar_number('select nvl(max(ID), 0) + 1 from RABAEV.RRL_TRANSPORT_TASK'));
  move_sequence_after('RRL_TR_VEHICLE_SQ', scalar_number('select nvl(max(ID), 0) + 1 from RABAEV.RRL_TR_VEHICLE'));
  move_sequence_after('RRL_TR_VODITEL_SQ', scalar_number('select nvl(max(ID), 0) + 1 from RABAEV.RRL_TR_VODITEL'));

  execute immediate
    'select nvl(max("' || unistr('\FFFD\FFFD\FFFD') || '"), 0) from RABAEV.SFERA_EAN'
    into sfera_max_id;
  move_sequence_after('SFERA_EAN_ID', sfera_max_id + 1);
end;
/
