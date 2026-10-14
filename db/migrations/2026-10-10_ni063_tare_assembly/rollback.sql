declare n number;begin select count(*) into n from RRL_TARE_BOOK;if n>0 then raise_application_error(-20808,'TARE_BOOK_HISTORY_RECONCILIATION_REQUIRED');end if;end;
/
drop trigger RRL_TARE_BOOK_GUARD;
/
drop trigger RRL_CASE_TARE_START_GUARD;
/
drop trigger RRL_HU_TARE_LINK_GUARD;
/
drop trigger RRL_HU_TARE_WARE_GUARD;
/
@@../2026-10-08_stock_posting_core/408_checkpoint_before_tare_assembly.sql
@@../2026-10-08_stock_posting_core/409_checkpoint_before_tare_assembly.sql
@@../2026-10-08_stock_posting_core/410_checkpoint_before_tare_assembly.sql
@@../2026-10-10_ni063_tare_resolution/007_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
