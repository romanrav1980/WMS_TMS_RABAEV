-- Physical history must not become an untracked quantity after downgrade.
declare n number;begin select count(*)into n from RRL_SKU_RECEIPT_POLICY where SERIALIZED_WEIGHT_BOXES=1;
if n>0 then raise_application_error(-20808,'WEIGHT_BOX_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_root.sql
@@000_before_unit.sql
-- Keep additive default0 column/read decoder; no quantity or physical history deletion.
@@../2026-10-08_stock_posting_core/014b_recompile.sql
