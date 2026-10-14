declare n number;begin select count(*)into n from RRL_INTERWARE_PLAN;if n>0 then raise_application_error(-20808,'INTERWARE_PLAN_FORWARD_REVISION_REQUIRED');end if;execute immediate 'drop trigger RRL_STORE_INTERWARE_LEG_GUARD';execute immediate 'drop table RRL_INTERWARE_PLAN';end;
/
@@../2026-10-08_stock_posting_core/429_before118_metadata.sql
