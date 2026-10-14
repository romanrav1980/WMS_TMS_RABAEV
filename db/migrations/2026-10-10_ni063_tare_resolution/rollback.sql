-- Keep resolution facts; reverting view after real resolutions requires reconciliation.
declare n number;begin select count(*) into n from RRL_TARE_RESOLUTION;if n>0 then raise_application_error(-20808,'TARE_RESOLUTION_HISTORY_RECONCILIATION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/406_checkpoint_before_tare_resolution.sql
@@../2026-10-08_stock_posting_core/407_checkpoint_before_tare_resolution.sql
@@../2026-10-10_ni063_tare_deadlines/004_debt_view.sql
@@../2026-10-10_ni063_tare_ledger/006_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
