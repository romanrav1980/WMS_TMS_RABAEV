declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_DISPATCH_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_DISPATCH_SOURCE_IX on RRL_INTERWARE_ONWARD_DISPATCH(SOURCE_LOAD_OPERATION_ID,OPERATION_ID)';end if;
 dbms_stats.gather_table_stats(user,'RRL_INTERWARE_ONWARD_DISPATCH',cascade=>true);
end;
/
