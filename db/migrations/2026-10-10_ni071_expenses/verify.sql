declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_LOG_EXP_ARTICLE_GUARD','RRL_LOG_EXPENSE_GUARD','RRL_LOG_EXP_DECISION_GUARD')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'LOGISTICS_EXPENSE_INVALID');end if;end;
/
