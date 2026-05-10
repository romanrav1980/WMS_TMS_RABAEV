prompt [13] CROSS_DOCKING compatibility package

create or replace package CROSS_DOCKING is
  function SYNC_SBORKA_PALL(sb_pall_uid varchar2) return int;
  function SYNC_ARTICUL(articul1 varchar2) return int;
  function SYNC_MOD(mod_id1 int) return int;
  function SYNC_SBOR_PALL_ROW(row_id1 int) return int;
end CROSS_DOCKING;
/

create or replace package body CROSS_DOCKING is
  function SYNC_ARTICUL(articul1 varchar2) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_articuls where acticul = articul1;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_MOD(mod_id1 int) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_articul_mods where id = mod_id1 and nvl(deleted, 0) = 0;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_SBOR_PALL_ROW(row_id1 int) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_sborka_pallet_rows where id = row_id1;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_SBORKA_PALL(sb_pall_uid varchar2) return int is
    v_condition number;
    v_prooved number;
    v_scan number;
    v_synced number;
  begin
    select nvl(condition, 0), nvl(prooved, 0), nvl(prooved_by_scan, 0), nvl(kross_syncronized, 0)
      into v_condition, v_prooved, v_scan, v_synced
      from rrl_sborka_pallets
     where pallet_uid = sb_pall_uid;

    if v_condition <> 2 and v_prooved <> 1 and v_scan <> 1 then
      return -1;
    end if;

    if v_synced = 1 then
      return 1;
    end if;

    update rrl_sborka_pallets set kross_syncronized = 1 where pallet_uid = sb_pall_uid;
    return 2;
  exception
    when no_data_found then return -3;
    when others then return -3;
  end;
end CROSS_DOCKING;
/
