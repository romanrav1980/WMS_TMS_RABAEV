declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_INTERWARE_PLAN'and COLUMN_NAME='SOURCE_PLACE_UID';
 if n=0 then execute immediate 'alter table RRL_INTERWARE_PLAN add(SOURCE_PLACE_UID varchar2(200),SOURCE_HU_JSON clob check(SOURCE_HU_JSON is json))';end if;
end;
/
