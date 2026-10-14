declare n number;begin
select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK' and COLUMN_NAME='HU_MEASUREMENTS_JSON';
if n=0 then execute immediate 'alter table RRL_WAREHOUSE_TASK add HU_MEASUREMENTS_JSON clob check(HU_MEASUREMENTS_JSON is json)';end if;
select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_WARE_SETTINGS' and COLUMN_NAME='HU_CELL_HEIGHT_UNIT';
if n=0 then execute immediate 'alter table RRL_RECEIPT_WARE_SETTINGS add HU_CELL_HEIGHT_UNIT varchar2(2) check(HU_CELL_HEIGHT_UNIT in(''M'',''CM'',''MM''))';end if;
end;
/
