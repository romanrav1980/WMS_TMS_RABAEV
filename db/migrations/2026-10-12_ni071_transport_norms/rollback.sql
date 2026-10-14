declare n number;begin select count(*)into n from RRL_TRANSPORT_NORM_HISTORY;
 if n!=0 then raise_application_error(-20886,'TRANSPORT_NORM_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
drop trigger RRL_TRANSPORT_NORM_HIST_G;
drop trigger RRL_TRANSPORT_NORM_HEAD_G;
drop package RRL_TRANSPORT_NORM_API;
drop table RRL_TRANSPORT_NORM_HISTORY;
drop table RRL_TRANSPORT_NORM_HEAD;
-- Existing RRL_TRANSPORT_PRICE, carrier prices and stock are untouched.
