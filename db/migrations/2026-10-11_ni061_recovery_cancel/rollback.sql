declare n number;begin select count(*)into n from RRL_IW_RECOVERY_CANCEL;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_CANCELLATIONS_REQUIRE_FORWARD_FIX');end if;end;
/
@@../2026-10-11_ni061_recovery_placement/008_root_body.sql
@@../2026-10-11_ni061_partial_recovery/002_decisions_current.sql
@@../2026-10-11_ni061_partial_recovery/003_receiving_current.sql
drop trigger RRL_IW_REC_CANCEL_G;
drop package RRL_STOCK_IW_RECOVERY_CANCEL;
drop table RRL_IW_RECOVERY_CANCEL;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
