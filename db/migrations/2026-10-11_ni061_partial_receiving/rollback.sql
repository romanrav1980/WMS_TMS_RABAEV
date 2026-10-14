declare n number;begin select count(*)into n from RRL_INTERWARE_RECEIPT where ORIGINAL_ROOT_UID is not null;if n>0 then raise_application_error(-20886,'INTERWARE_PARTIAL_HISTORY_RETAINED');end if;end;
/
@@011_rollback_receiving_body.sql
@@000_before_rrl_stock_interware_put_body.sql
@@000_before_rrl_stock_interware_custody_body.sql
@@000_before_rrl_interware_depart_gate_body.sql
@@010_before_sap_guard.sql
drop package RRL_STOCK_INTERWARE_PART;
@@008_recompile.sql
-- Nullable additive columns are retained for paired application readers.
-- Native rollback explicitly refuses partial payloads; no silent full-mode reinterpretation.
