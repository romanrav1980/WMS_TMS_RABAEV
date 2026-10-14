declare n number;begin select count(*) into n from RRL_TARE_LOSS_CLAIM;if n>0 then raise_application_error(-20808,'LOSS_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@../2026-10-08_stock_posting_core/414_before105_root.sql
@@../2026-10-08_stock_posting_core/415_before105_planning.sql
@@../2026-10-10_ni063_tare_assembly/001_schema.sql
@@../2026-10-10_ni063_tare_assembly/007_balance_guards.sql
