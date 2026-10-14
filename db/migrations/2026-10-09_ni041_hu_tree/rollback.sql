-- Only while no live links/containers exist; preserve history otherwise.
declare n number;begin select count(*) into n from RRL_WMS_HU_LINK;
if n>0 then raise_application_error(-20886,'HU_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@../2026-10-08_stock_posting_core/304_checkpoint_hu_posting.sql
@@../2026-10-08_stock_posting_core/301_checkpoint_hu_balance.sql
@@../2026-10-08_stock_posting_core/302_checkpoint_hu_closure.sql
@@../2026-10-08_stock_posting_core/303_checkpoint_hu_eligibility.sql
drop package RRL_STOCK_HU_CMD;
/
drop package RRL_STOCK_HU_READ;
/
drop trigger RRL_HU_CONTAINER_GUARD;
/
drop table RRL_WMS_HU_LINK;
/
drop sequence RRL_WMS_HU_LINK_SQ;
/
-- Existing additive columns remain; do not drop operational identities.
@@../2026-10-08_stock_posting_core/014b_recompile.sql
