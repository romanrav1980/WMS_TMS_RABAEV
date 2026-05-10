prompt [08] REMAINS compatibility package for WindowsApplication2
create or replace package REMAINS is
  function create_snapshot(type2 int) return int;
  function close_snapshot(snap_shot_id1 int) return int;
  function add_row_2_snapshot(snap_shot_id1 int, cell1 varchar, articul1 varchar2) return int;
  function remains_free(articul1 varchar2) return number;
  function remains_in_otbor(articul1 varchar2) return number;
  function remains_in_otbor_all(articul1 varchar2) return number;
  function remains_free_all(articul1 varchar2) return number;
  function remains_partion_in_cell(pallet_uid1 varchar2, cell3 varchar2) return number;
  function remains_partion_in_otbor(pallet_uid1 varchar2) return number;
  function remains_except_part_in_otb(pallet_uid1 varchar2) return number;
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2) return varchar2;
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2) return int;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2) return int;
  function othod_pallet_podbor_partii(PALLET_ID1 varchar2) return int;
  function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2) return varchar2;
  function close_othod_pall_row(PALLET_ROW_ID1 int, prih_pall_uid5 varchar2, kolvo_provod number, iser_id21 varchar2) return int;
  function OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1 varchar2, cell1 varchar2) return int;
  function get_remains_text(articul1 varchar2) return varchar2;
  function turnover_now(articul1 varchar2) return number;
  function remains_of_prihods(articul1 varchar2, d_from date, d_to date) return number;
  function storno_op(pall_uid1 varchar2, user_id1 varchar2) return int;
end REMAINS;
/
create or replace package body REMAINS is
  function create_snapshot(type2 int) return int is
    id1 int;
  begin
    select RRL_REMAIN_SNAPSHOT_SQ.nextval into id1 from dual;
    insert into RRL_REMAIN_SNAPSHOT (ID, TYPE1, CREATE_TIME, SNAP_SHOT_TIME, CLOSED)
    values (id1, type2, systimestamp, systimestamp, 0);
    return id1;
  end;
  function add_row_2_snapshot(snap_shot_id1 int, cell1 varchar, articul1 varchar2) return int is
    tmp int;
    ware_id1 int;
    id1 int;
    snap_time1 date;
    cursor sss is
      select rm.uid_poleta, rm.remain
        from rrl_remains rm
        join rrl_pallets pts on pts.uid_pallet = rm.uid_poleta
       where rm.cell = cell1
         and pts.articul = articul1;
  begin
    if cell1 is null or articul1 is null then
      return -1;
    end if;
    select closed, snap_shot_time into tmp, snap_time1
      from RRL_REMAIN_SNAPSHOT where ID = snap_shot_id1;
    if tmp = 1 then
      return -1;
    end if;
    begin
      select ID into id1 from RRL_REMAIN_SNAPSHOT_ROWS
       where ARTICUL = articul1 and CELL = cell1 and SNAP_SHOT_ID = snap_shot_id1;
      return id1;
    exception when no_data_found then null;
    end;
    select ware_id into ware_id1 from rrl_cells where cell = cell1;
    for s in sss loop
      select RRL_REMAIN_SNAPSHOT_ROWS_SQ.nextval into id1 from dual;
      insert into RRL_REMAIN_SNAPSHOT_ROWS (ID, ARTICUL, CELL, PALLET_UID, REMAIN, WARE_ID, CONDITION, SNAP_SHOT_ID, SNAP_TIME)
      values (id1, articul1, cell1, s.uid_poleta, s.remain, ware_id1, 0, snap_shot_id1, snap_time1);
    end loop;
    return 1;
  exception
    when no_data_found then return -2;
  end;
  function close_snapshot(snap_shot_id1 int) return int is
    time_shot date;
  begin
    time_shot := systimestamp;
    update RRL_REMAIN_SNAPSHOT set CLOSED = 1, SNAP_SHOT_TIME = time_shot where ID = snap_shot_id1;
    return 1;
  end;
  function remains_free(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_cells cel on rem.cell = cel.cell
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where cel.blocked_for_remains = 0
       and pts.articul = articul1
       and rem.remain > 0
       and nvl(cel.otbor, 0) = 0;
    return tmp;
  exception when others then return 0; end;
  function remains_in_otbor(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_cells cel on rem.cell = cel.cell
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where pts.articul = articul1
       and rem.remain > 0
       and nvl(cel.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function remains_in_otbor_all(articul1 varchar2) return number is
  begin
    return remains_in_otbor(articul1);
  end;
  function remains_free_all(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where pts.articul = articul1
       and rem.remain > 0;
    return tmp;
  exception when others then return 0; end;
  function remains_partion_in_cell(pallet_uid1 varchar2, cell3 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(remain), 0) into tmp
      from rrl_remains
     where uid_poleta = pallet_uid1
       and cell = cell3
       and remain > 0;
    return tmp;
  exception when others then return 0; end;
  function remains_partion_in_otbor(pallet_uid1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_cells cl on rm.cell = cl.cell
     where rm.uid_poleta = pallet_uid1
       and rm.remain > 0
       and nvl(cl.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function remains_except_part_in_otb(pallet_uid1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_cells cl on rm.cell = cl.cell
      join rrl_pallets p on rm.uid_poleta = p.uid_pallet
      join rrl_pallets src on src.uid_pallet = pallet_uid1
     where p.articul = src.articul
       and rm.uid_poleta <> pallet_uid1
       and rm.remain > 0
       and nvl(cl.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2) return varchar2 is
  begin
    return RRL_CLOSE_OTHOD_PALLET(PALLET_ID1, iser_id21);
  end;
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2) return int is
  begin
    return RRL_TRIAL_BY_WEIGHT(PALLET_UID1, TRIAL_WEIGHT1, WOOD_WEIGHT1, user_id1);
  end;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2) return int is
  begin
    return RRL_SET_SCAN_PROOVE2(PALLET_UID1, count_of_errors1, prim1, SBORSHIK1, KLADOVSHIK1);
  end;
  function OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1 varchar2, cell1 varchar2) return int is
    tmpVar int;
    current_cell varchar2(50);
    kolvo_otbora number;
    count_of_PUID int;
    mod_id4 int;
    articul_for varchar2(255);
    cursor rowss is
      select * from RRL_SBORKA_PALLET_ROWS rs where rs.PALLET_UID = PALLET_ID1;
    cursor rests_in_cell is
      select rm.remain, rm.uid_poleta, p.expiry_date, p.articul
        from rrl_remains rm join rrl_pallets p on rm.uid_poleta = p.uid_pallet
       where rm.cell = current_cell and rm.remain > 0 and p.articul = articul_for
       order by p.expiry_date;
  begin
    select condition into tmpVar from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1;
    if tmpVar >= 2 then return -1; end if;
    for naklad_row in rowss loop
      count_of_PUID := 0;
      kolvo_otbora := naklad_row.quantity;
      articul_for := naklad_row.articul;
      current_cell := cell1;
      for ddd8 in rests_in_cell loop
        exit when kolvo_otbora <= 0;
        count_of_PUID := count_of_PUID + 1;
        select PPP.MOD_ID into mod_id4 from RRL_PALLETS PPP where PPP.UID_PALLET = ddd8.UID_POLETA;
        update RRL_SBORKA_PALLET_ROWS
           set CURRENT_MOD_ID = mod_id4,
               PRIHOD_PALLET_UID = ddd8.UID_POLETA,
               PRIHOD_PALLET_UID_COUNT = count_of_PUID,
               EXPIRY_DATE = ddd8.EXPIRY_DATE
         where ID = naklad_row.ID;
        kolvo_otbora := 0;
      end loop;
    end loop;
    return 1;
  exception when no_data_found then return 0; end;
  function othod_pallet_podbor_partii(PALLET_ID1 varchar2) return int is
    return_supplier_id1 varchar2(255);
    tmpVar int;
    current_cell varchar2(50);
    kolvo_otbora number;
    count_of_PUID int;
    mod_id4 int;
    articul_for varchar2(255);
    cursor rowss is
      select * from RRL_SBORKA_PALLET_ROWS rs
       where rs.PALLET_UID = PALLET_ID1
         and (
           rs.PRIHOD_PALLET_UID is null or
           remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) <= 0 or
           (remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) is null and remains_except_part_in_otb(rs.PRIHOD_PALLET_UID) > 0)
         );
    cursor rests_in_cell is
      select rm.remain, rm.uid_poleta, p.expiry_date, p.articul
        from rrl_remains rm join rrl_pallets p on rm.uid_poleta = p.uid_pallet
       where rm.cell = current_cell and rm.remain > 0 and p.articul = articul_for
       order by p.expiry_date;
  begin
    select condition, return_supplier_id into tmpVar, return_supplier_id1
      from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1;
    if return_supplier_id1 is not null then
      return OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1, 'RETURNS');
    end if;
    if tmpVar >= 2 then return -1; end if;
    for naklad_row in rowss loop
      count_of_PUID := 0;
      kolvo_otbora := naklad_row.quantity;
      articul_for := naklad_row.articul;
      select cell into current_cell from RRL_ARTICULS where ACTICUL = naklad_row.articul;
      for ddd8 in rests_in_cell loop
        exit when kolvo_otbora <= 0;
        count_of_PUID := count_of_PUID + 1;
        select PPP.MOD_ID into mod_id4 from RRL_PALLETS PPP where PPP.UID_PALLET = ddd8.UID_POLETA;
        update RRL_SBORKA_PALLET_ROWS
           set CURRENT_MOD_ID = mod_id4,
               PRIHOD_PALLET_UID = ddd8.UID_POLETA,
               PRIHOD_PALLET_UID_COUNT = count_of_PUID,
               EXPIRY_DATE = ddd8.EXPIRY_DATE
         where ID = naklad_row.ID;
        kolvo_otbora := 0;
      end loop;
    end loop;
    return 1;
  exception when no_data_found then return 0; end;
  function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2) return varchar2 is
    articul1 varchar2(50);
    cell1 varchar2(50);
    count1 number;
    tmp varchar2(50);
  begin
    begin
      select pts.articul, pts.unit_count into articul1, count1 from rrl_pallets pts where pts.uid_pallet = pall_uid1;
    exception when no_data_found then return 'no_pall'; end;
    select art.cell into cell1 from rrl_articuls art where art.acticul = articul1;
    tmp := RABAEV.RRL_INTERNAL_MOVE3(pallet_id => pall_uid1, cell_to => cell1, count1 => count1, user_id1 => user_id2);
    return tmp;
  exception when others then return 'error'; end;
  function close_othod_pall_row(PALLET_ROW_ID1 int, prih_pall_uid5 varchar2, kolvo_provod number, iser_id21 varchar2) return int is
  begin
    return 1;
  end;
  function get_remains_text(articul1 varchar2) return varchar2 is
  begin
    return ' [' || to_char(nvl(remains_free_all(articul1), 0)) || ']';
  end;
  function turnover_now(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rs.quantity), 0) into tmp
      from rrl_sborka_pallet_rows rs
      join rrl_sborka_pallets sp on rs.pallet_uid = sp.pallet_uid
     where rs.articul = articul1
       and nvl(sp.checking_time, sp.create_date) >= systimestamp - 30;
    return tmp;
  exception when others then return 0; end;
  function remains_of_prihods(articul1 varchar2, d_from date, d_to date) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_pallets p on rm.uid_poleta = p.uid_pallet
     where p.articul = articul1
       and rm.remain > 0
       and nvl(p.creation_date, sysdate) >= d_from
       and nvl(p.creation_date, sysdate) < d_to;
    return tmp;
  exception when others then return 0; end;
  function storno_op(pall_uid1 varchar2, user_id1 varchar2) return int is
    tt_id1 int;
    tt_cond varchar2(255);
  begin
    begin
      select transtask_id into tt_id1 from rrl_sborka_pallets where pallet_uid = pall_uid1;
    exception when no_data_found then return -2; end;
    if tt_id1 is not null then
      begin
        select condition into tt_cond from rrl_transport_task where id = tt_id1;
        if tt_cond = '???????' then
          return -3;
        end if;
      exception when no_data_found then null; end;
    end if;
    update rrl_sborka_pallets
       set prooved = 0,
           prooved_by_scan = 0,
           checking_time = null,
           kladovshik = user_id1,
           trial_weight = null,
           wood_weight = null,
           count_of_errors = null,
           prim = null
     where pallet_uid = pall_uid1;
    return 1;
  end;
begin
  null;
end REMAINS;
/
alter package REMAINS compile;
alter package REMAINS compile body;

