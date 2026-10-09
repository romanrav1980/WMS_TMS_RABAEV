declare n number;
 procedure add_col(p_col varchar2,p_type varchar2) is begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PALLETS' and COLUMN_NAME=p_col;
 if n=0 then execute immediate 'alter table RRL_PALLETS add ('||p_col||' '||p_type||')';end if;
 end;
begin
 add_col('STOCK_ORIGIN_UID','varchar2(200)');
 add_col('CREATED_BY_STOCK_OP','varchar2(100)');
end;
/
