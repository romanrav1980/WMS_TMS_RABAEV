declare n number;begin select count(*)into n from RRL_HU_PACK_CYCLE;
 if n!=0 then raise_application_error(-20886,'BOX_PACKING_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_hu_cmd.sql
@@000_before_rrl_stock_hu_read.sql
drop trigger RRL_HU_PACK_CYCLE_GUARD;
drop package RRL_HU_PACK_CLOCK;
drop table RRL_HU_PACK_CYCLE;
-- Preserve all APPLIED inventory and shipping facts; no historical clock deletion.
