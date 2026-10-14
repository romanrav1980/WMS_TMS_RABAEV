declare n number;begin select count(*)into n from RRL_STORE_CASE_CLOSURE;if n>0 then raise_application_error(-20808,'STORE_CASE_CLOSURE_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/428_before117_case_work.sql
@@../2026-10-10_ni062_case_work/004_guards.sql
