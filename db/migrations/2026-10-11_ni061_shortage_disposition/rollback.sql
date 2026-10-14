declare n number;begin
 select count(*)into n from RRL_INTERWARE_SHORTAGE_REQUEST;if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_SHORTAGE_HISTORY');end if;
end;
/
@@000_before_rrl_stock_posting_api_package_body.sql
@@../2026-10-11_ni061_marked_partial/001_unit_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
-- Preserve additive empty tables for current read projections; revert app/UI before schema removal.
