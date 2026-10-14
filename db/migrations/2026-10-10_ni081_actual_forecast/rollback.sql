declare n number;begin select count(*)into n from RRL_FORECAST_LOAD;if n!=0 then raise_application_error(-20899,'FORECAST133_SOURCE_HISTORY_FORWARD_ONLY');end if;end;
/
drop table RRL_FORECAST_SKU_DAY;
drop table RRL_FORECAST_DAY;
drop table RRL_FORECAST_CASE_ORIGIN;
drop table RRL_FORECAST_LEAF;
drop table RRL_FORECAST_LOAD;
drop package RRL_FORECAST_PROJECTOR;
drop package RRL_FORECAST_SOURCE_RULES;
drop index RRL_LOAD_FORECAST_WD_I1;
