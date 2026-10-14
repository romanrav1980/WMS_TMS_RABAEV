declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SLOT_CLAIM' and COLUMN_NAME='HU_STOCK_COMPOSITION_VERSION';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_SLOT_CLAIM add HU_STOCK_COMPOSITION_VERSION number(19)';end if;
end;
/
