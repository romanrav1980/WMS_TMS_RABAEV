declare n number;begin select count(*)into n from RRL_LOGISTICS_EXPENSE;if n>0 then raise_application_error(-20808,'LOGISTICS_EXPENSE_FORWARD_CORRECTION_REQUIRED');end if;execute immediate 'drop table RRL_LOGISTICS_EXP_DECISION';execute immediate 'drop table RRL_LOGISTICS_EXPENSE';execute immediate 'drop table RRL_LOGISTICS_EXP_ARTICLE';end;
/
