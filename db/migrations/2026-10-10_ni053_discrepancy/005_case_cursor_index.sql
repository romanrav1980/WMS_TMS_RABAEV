declare n number;
begin
 select count(*) into n from user_indexes where index_name='RRL_STORE_CASE_ADDR_CURSOR';
 if n=0 then execute immediate 'create index RRL_STORE_CASE_ADDR_CURSOR on RRL_STORE_DISCREPANCY_CASE(STORE_ADDR,CASE_ID)';end if;
end;
/
