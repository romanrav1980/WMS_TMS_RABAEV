declare n number;begin select count(*) into n from RRL_TARE_OFFER_BOOK;if n>0 then raise_application_error(-20808,'TARE_BOOKED_HANDOVER_HISTORY_RECONCILIATION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/411_checkpoint_before_booked_handover.sql
@@../2026-10-10_ni063_tare_assembly/008_book_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
