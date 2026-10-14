declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PALLETS' and COLUMN_NAME='STOCK_COMPOSITION_VERSION';
 if n=0 then execute immediate 'alter table RRL_PALLETS add STOCK_COMPOSITION_VERSION number default 0 not null check(STOCK_COMPOSITION_VERSION>=0 and STOCK_COMPOSITION_VERSION=trunc(STOCK_COMPOSITION_VERSION))';end if;
end;
/
