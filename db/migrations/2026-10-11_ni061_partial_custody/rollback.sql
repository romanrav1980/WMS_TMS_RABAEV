declare n number;begin
 select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.ORIGINAL_ROOT_UID is not null;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_PARTIAL_CUSTODY');end if;
end;
/
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_stock_interware_custody_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_stock_interware_next_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_interware_depart_gate_package_body.sql
@@000_before_load_fact_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
