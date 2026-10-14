declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_TRANSPORT_COST_DETAIL'and CONSTRAINT_NAME='RRL_TRAN_COST_AMOUNT_CK';
 if n=0 then execute immediate 'alter table RRL_TRANSPORT_COST_DETAIL add constraint RRL_TRAN_COST_AMOUNT_CK check(AMOUNT=round(QUANTITY*RATE_VALUE,2))';end if;
 for r in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_TRANSPORT_COST_DETAIL'and CONSTRAINT_TYPE='C'
  and CONSTRAINT_NAME!='RRL_TRAN_COST_AMOUNT_CK'and upper(SEARCH_CONDITION_VC)like '%AMOUNT%'and upper(SEARCH_CONDITION_VC)like '%ROUND%')loop
  execute immediate 'alter table RRL_TRANSPORT_COST_DETAIL drop constraint '||dbms_assert.simple_sql_name(r.CONSTRAINT_NAME);
 end loop;
end;
/
