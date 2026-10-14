declare n number;begin select count(*)into n from RRL_TARE_LOAD_RECOVERY;if n>0 then raise_application_error(-20863,'TARE_LOAD_RECOVERY_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_root.sql
@@000_before_book.sql
@@000_before_unload.sql
drop package RRL_TARE_LOAD_RECOVERY_API;
drop table RRL_TARE_LOAD_RECOVERY;
drop index RRL_TARE_OFFER_BOOK_LOAD_IX;
