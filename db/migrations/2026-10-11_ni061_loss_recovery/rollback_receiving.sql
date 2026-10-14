declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT;if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_PHYSICAL_RECOVERY');end if;
end;
/
@@004_decision_root_body.sql
@@000_before_rrl_stock_balance_core_package.sql
@@000_before_rrl_stock_location_core_package.sql
@@000_before_rrl_stock_interware_part_package.sql
@@000_before_rrl_stock_unit_core_package.sql
@@000_before_rrl_stock_unit_core_package_body.sql
@@000_before_rrl_stock_unit_guard.sql
@@../2026-10-11_ni061_partial_receiving/007_sap_clone_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
