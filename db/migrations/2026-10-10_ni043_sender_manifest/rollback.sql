declare n number;begin select(select count(*)from RRL_TRACE_MANIFEST_USE)+(select count(*)from RRL_TRACE_SENDER_MANIFEST)into n from dual;if n!=0 then raise_application_error(-20899,'TRACE124_SOURCE_HISTORY_FORWARD_ONLY');end if;end;
/
drop table RRL_TRACE_MANIFEST_USE;
drop table RRL_TRACE_SENDER_AGG;
drop table RRL_TRACE_SENDER_MANIFEST;
@@../2026-10-08_stock_posting_core/441_before124_metadata.sql
