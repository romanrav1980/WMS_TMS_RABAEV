declare n number;begin select count(*)into n from RRL_CASE_SSCC_LABEL;if n>0 then raise_application_error(-20863,'CASE_SSCC_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_case.sql
drop trigger RRL_CASE_SSCC_ID_GUARD;
drop trigger RRL_CASE_SSCC_LABEL_GUARD;
drop context RRL_CASE_SSCC_CTX;
drop package RRL_CASE_SSCC_API;
drop package RRL_SSCC_ALLOCATOR;
drop table RRL_CASE_SSCC_LABEL;
