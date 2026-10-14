declare n number;begin select count(*)into n from RRL_RETURN_DISPOSAL_FACT;if n>0 then raise_application_error(-20808,'RETURN_DISPOSAL_FORWARD_CORRECTION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/426_before110_root.sql
@@../2026-10-08_stock_posting_core/427_before110_effect.sql
