declare n number;begin select count(*)into n from RRL_LOGISTICS_RATE_HISTORY where COMPONENTS_JSON is not null;if n>0 then raise_application_error(-20899,'MONTHLY_RATE_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_history_guard.sql
