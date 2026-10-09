declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_METADATA_TX authid definer as
 procedure begin_change(p_actor varchar2,p_permission varchar2);
 procedure end_change;
end;
/

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
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2,p_operation_id varchar2 default null) return varchar2;
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2) return int;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2) return int;
  function othod_pallet_podbor_partii(PALLET_ID1 varchar2) return int;
  function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2,p_operation_id varchar2 default null) return varchar2;
  function close_othod_pall_row(PALLET_ROW_ID1 int, prih_pall_uid5 varchar2, kolvo_provod number, iser_id21 varchar2) return int;
  function OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1 varchar2, cell1 varchar2) return int;
  function get_remains_text(articul1 varchar2) return varchar2;
  function turnover_now(articul1 varchar2) return number;
  function remains_of_prihods(articul1 varchar2, d_from date, d_to date) return number;
  function storno_op(pall_uid1 varchar2, user_id1 varchar2) return int;
end REMAINS;
/

create or replace package body RRL_STOCK_METADATA_TX as
 procedure begin_change(p_actor varchar2,p_permission varchar2) is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();state varchar2(20);
 begin
  if p_actor is null or p_permission is null or p_permission not in('warehouse_task_assign','warehouse_task_edit','case_pick_execute','case_pick_short_approve')
   or RRL_HAS_WRIGHT(p_actor,p_permission)!=1 then raise_application_error(-20882,'TASK_METADATA_FORBIDDEN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state is null or state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'TASK_METADATA_RELEASE_CLOSED');end if;
 end;
 procedure end_change is begin RRL_STOCK_LOCK_API.clear_plan;end;
end;
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
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2,p_operation_id varchar2 default null) return varchar2 is
  begin
    return RRL_CLOSE_OTHOD_PALLET(PALLET_ID1, iser_id21,p_operation_id);
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
function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2,p_operation_id varchar2 default null) return varchar2 is

 v_state varchar2(20);wire clob;result clob;d json_object_t:=json_object_t();m json_object_t:=json_object_t();s json_object_t:=json_object_t();
 article varchar2(160);target_cell varchar2(60);old_actor varchar2(100);
  function legacy_move(pall_uid1 varchar2, user_id2 varchar2) return varchar2 is
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

begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return legacy_move(pall_uid1,user_id2);end if;
 if p_operation_id is null or user_id2 is null or pall_uid1 is null then raise_application_error(-20871,'OPERATION_ID_AND_ACTOR_REQUIRED');end if;
 begin
  select CANONICAL_REQUEST,ACTOR into wire,old_actor from RRL_STOCK_OPERATION where OPERATION_ID=p_operation_id;
  d:=json_object_t.parse(wire);
  if old_actor!=user_id2 or d.get_string('command_type')!='INTERNAL_MOVE'
   or d.get_object('metadata').get_string('uid')!=pall_uid1
   or d.get_object('source').get_string('type')!='ARTICLE_PICK_CELL' then raise_application_error(-20872,'OPERATION_CONTENT_CONFLICT');end if;
 exception when no_data_found then
  select ARTICUL into article from RRL_PALLETS where UID_PALLET=pall_uid1;
  select CELL into target_cell from RRL_ARTICULS where ACTICUL=article;
  if target_cell is null then raise_application_error(-20886,'ARTICLE_PICK_CELL_REQUIRED');end if;
  d.put('contract_version',2);d.put('operation_id',p_operation_id);d.put('command_type','INTERNAL_MOVE');d.put('actor',user_id2);
  s.put('type','ARTICLE_PICK_CELL');d.put('source',s);d.put('lines',json_array_t());d.put('units',json_array_t());
  m.put_null('unit');m.put('uid',pall_uid1);m.put('target_cell',target_cell);m.put('quantity','0');d.put('metadata',m);
 end;
 RRL_STOCK_NATIVE_API.post(d.to_clob,user_id2,result);
 return 'ok_'||d.get_object('metadata').get_string('target_cell');
end;
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
