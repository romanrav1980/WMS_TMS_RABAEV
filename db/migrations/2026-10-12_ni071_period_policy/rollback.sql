declare n number;begin
 select count(*)into n from RRL_LOG_COST_PERIOD_HISTORY;if n>0 then raise_application_error(-20899,'FINANCIAL_PERIOD_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;
 select count(*)into n from RRL_LOGISTICS_COST_LINE where PERIOD_MODE is not null;if n>0 then raise_application_error(-20899,'FINANCIAL_PERIOD_CHARGE_REQUIRES_FORWARD_RECOVERY');end if;
end;
/
@@000_before_cost_guard.sql
drop trigger RRL_LOG_COST_PERIOD_HEAD_G;
drop trigger RRL_LOG_COST_PERIOD_HISTORY_G;
drop table RRL_LOG_COST_PERIOD_HISTORY;
drop table RRL_LOG_COST_PERIOD_HEAD;
