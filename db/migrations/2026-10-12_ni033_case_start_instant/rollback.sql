declare n number;begin select count(*)into n from RRL_CASE_PICK_TASK where STARTED_AT_INSTANT is not null;if n>0 then raise_application_error(-20899,'ACTUAL_CASE_START_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
drop trigger RRL_CASE_START_TIME_GUARD;
