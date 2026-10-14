declare n number;begin select count(*)into n from RRL_INTERWARE_ONWARD_BIND;if n!=0 then raise_application_error(-20899,'INTERWARE122_FACTS_FORWARD_ONLY');end if;end;
/
drop trigger RRL_INTERWARE_ONWARD_ROW_GUARD;
drop trigger RRL_INTERWARE_ONWARD_ST_GUARD;
@@../2026-10-08_stock_posting_core/440_before122_shipping.sql
drop table RRL_INTERWARE_ONWARD_DISPATCH;
drop table RRL_INTERWARE_ONWARD_BIND;
drop package RRL_STOCK_INTERWARE_NEXT;
