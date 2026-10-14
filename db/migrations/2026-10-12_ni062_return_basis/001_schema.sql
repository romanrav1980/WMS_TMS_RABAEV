declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_APPROVAL'and COLUMN_NAME='RETURN_BASIS';
 if n=0 then execute immediate q'[alter table RRL_STORE_RETURN_APPROVAL add(RETURN_BASIS varchar2(10)default 'ACCEPTED'not null check(RETURN_BASIS in('ACCEPTED','REFUSED','DAMAGED')))]';end if;
end;
/
