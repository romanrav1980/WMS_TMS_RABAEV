declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_LOGISTICS_RATE_HISTORY'and COLUMN_NAME='COMPONENTS_JSON';
 if n=0 then execute immediate 'alter table RRL_LOGISTICS_RATE_HISTORY add(COMPONENTS_JSON clob check(COMPONENTS_JSON is json))';end if;
end;
/
