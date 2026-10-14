declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK' and COLUMN_NAME='HU_CONTENT_VERSION';
 if n=0 then execute immediate 'alter table RRL_WAREHOUSE_TASK add HU_CONTENT_VERSION number';end if;
end;
/
@@../2026-10-09_ni041_hu_tree/001_schema.sql
