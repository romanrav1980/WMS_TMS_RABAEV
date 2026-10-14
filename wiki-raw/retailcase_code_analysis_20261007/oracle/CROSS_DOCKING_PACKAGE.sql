package CROSS_DOCKING is
  function SYNC_SBORKA_PALL(sb_pall_uid varchar2) return int;
  function SYNC_ARTICUL(articul1 varchar2) return int;
  function SYNC_MOD(mod_id1 int) return int;
  function SYNC_SBOR_PALL_ROW(row_id1 int) return int;
end CROSS_DOCKING;
