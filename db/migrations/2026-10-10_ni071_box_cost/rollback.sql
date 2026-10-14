declare n number;begin select count(*)into n from RRL_LOGISTICS_COST_RUN;if n>0 then raise_application_error(-20808,'LOGISTICS_COST_FORWARD_CORRECTION_REQUIRED');end if;execute immediate 'drop table RRL_LOGISTICS_COST_LINE';execute immediate 'drop table RRL_LOGISTICS_COST_RUN';execute immediate 'drop table RRL_LOGISTICS_RATE_HISTORY';execute immediate 'drop table RRL_LOGISTICS_RATE_HEAD';end;
/
