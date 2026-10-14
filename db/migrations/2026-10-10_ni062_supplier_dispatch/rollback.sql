declare n number;begin select count(*)into n from RRL_STORE_RETURN_SUP_DISPATCH;if n>0 then raise_application_error(-20808,'SUP_RETURN_DISPATCH_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/423_before108_shipping.sql
@@../2026-10-08_stock_posting_core/424_before108_effect.sql
