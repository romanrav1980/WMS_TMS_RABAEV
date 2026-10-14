declare n number;begin select count(*)into n from RRL_WARE_DEPOT_HISTORY;if n>0 then raise_application_error(-20886,'WARE_DEPOT_HISTORY_RETAINED');end if;end;
/
@@004_before_time_body.sql
@@006_before_metadata.sql
drop trigger RRL_WARE_DEPOT_GUARD;
drop package RRL_WARE_DEPOT_API;
drop table RRL_WARE_DEPOT_HISTORY;
