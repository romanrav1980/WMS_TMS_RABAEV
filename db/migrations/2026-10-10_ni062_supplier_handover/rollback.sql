declare n number;begin select count(*)into n from RRL_SUP_RETURN_HANDOVER;if n>0 then raise_application_error(-20808,'SUP_HANDOVER_FORWARD_REPAIR_REQUIRED');end if;execute immediate 'drop table RRL_SUP_RETURN_CONFIRM';execute immediate 'drop table RRL_SUP_RETURN_HANDOVER';end;
/
@@../2026-10-08_stock_posting_core/425_before109_metadata.sql
