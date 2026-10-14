declare n number;begin select(select count(*)from RRL_INTERWARE_RECEIPT)+(select count(*)from RRL_INTERWARE_UNLOAD)into n from dual;if n!=0 then raise_application_error(-20899,'INTERWARE119_FACTS_FORWARD_CORRECTION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/430_before119_root.sql
@@../2026-10-08_stock_posting_core/431_before119_balance.sql
@@../2026-10-08_stock_posting_core/432_before119_location.sql
drop table RRL_INTERWARE_RECEIPT;
drop table RRL_INTERWARE_UNLOAD;
drop package RRL_STOCK_INTERWARE_REC;
