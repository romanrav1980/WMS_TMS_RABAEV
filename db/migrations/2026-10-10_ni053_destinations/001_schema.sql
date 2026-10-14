declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_HU_LOAD_ST' and COLUMN_NAME='DESTINATION_ADDR';
 if n=0 then execute immediate 'alter table RRL_TT_HU_LOAD_ST add DESTINATION_ADDR varchar2(255)';end if;
end;
/
-- Old immutable loading facts are intentionally not populated from mutable current addresses.
