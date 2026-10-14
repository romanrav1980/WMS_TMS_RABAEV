-- Keep physical history: refuse downgrade once repacking was committed.
declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='HU_REPACK_SLOT'and STATE='APPLIED';if n>0 then raise_application_error(-20808,'HU_REPACK_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_hu.sql
@@000_before_placement.sql
@@000_before_reserve.sql
@@000_before_root.sql
@@000_before_rrl_hu_claim_measure_guard.sql
@@000_before_rrl_hu_container_guard.sql
@@000_before_rrl_hu_link_write_guard.sql
@@000_before_rrl_hu_tare_link_guard.sql
@@000_before_rrl_hu_task_plan_guard.sql
@@000_before_slot.sql
drop package RRL_STOCK_HU_REPACK_CMD;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
