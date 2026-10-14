declare n number;begin select count(*)into n from RRL_WAVE_TIME_PLAN;
 if n>0 then raise_application_error(-20899,'WAVE_TIME140_HISTORY_REQUIRES_FORWARD_FIX');end if;end;
/
drop trigger RRL_WAVE_TIME_PLAN_GUARD;
drop package RRL_WAVE_TIME_API;
drop table RRL_WAVE_TIME_PLAN;
/
