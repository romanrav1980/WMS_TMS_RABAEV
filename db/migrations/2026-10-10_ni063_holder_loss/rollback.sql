declare n number;begin select count(*)into n from RRL_TARE_LOSS_CLAIM where SOURCE_CLAIM_ID is not null or TRANSPORT_TASK_ID is not null;if n>0 then raise_application_error(-20808,'HOLDER_LOSS_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-10_ni063_tare_resolution/004_debt_view.sql
@@../2026-10-08_stock_posting_core/417_before106_loss.sql
@@../2026-10-08_stock_posting_core/418_before106_tare.sql
@@../2026-10-08_stock_posting_core/419_before106_resolution.sql
