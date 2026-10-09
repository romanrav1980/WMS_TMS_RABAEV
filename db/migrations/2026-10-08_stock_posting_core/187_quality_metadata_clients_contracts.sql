-- Rare metadata/placement changes take CONFIG X before any document or slot lock.
-- This grants no stock/configuration write context and cannot conduct quantities.
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
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2,p_operation_id varchar2 default null) return int;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2,p_operation_id varchar2 default null) return int;
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
