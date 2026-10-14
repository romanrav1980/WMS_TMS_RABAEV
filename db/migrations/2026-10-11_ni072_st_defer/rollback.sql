declare n number;begin select count(*)into n from RRL_ST_DEFER_DECISION;if n>0 then raise_application_error(-20886,'ST_DEFER_HISTORY_RETAINED');end if;end;
/
drop trigger RRL_ST_DEFER_GUARD;
drop package RRL_ST_DEFER_API;
drop table RRL_ST_DEFER_DECISION;
