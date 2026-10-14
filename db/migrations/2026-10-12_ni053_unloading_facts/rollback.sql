declare n number;begin select count(*)into n from RRL_STORE_UNLOAD_START;
 if n!=0 then raise_application_error(-20886,'UNLOAD_FACT_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_receipt.sql
drop trigger RRL_STORE_UNLOAD_FACT_G;
drop trigger RRL_STORE_UNLOAD_START_G;
drop package RRL_STORE_UNLOAD_CORE;
drop package RRL_STORE_UNLOAD_API;
drop table RRL_STORE_UNLOAD_FACT;
drop table RRL_STORE_UNLOAD_START;
-- Existing receipt, buyer facts, traceability, outbox and stock remain untouched.
