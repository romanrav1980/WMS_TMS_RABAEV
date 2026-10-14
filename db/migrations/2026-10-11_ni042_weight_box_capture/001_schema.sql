declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SKU_RECEIPT_POLICY'and COLUMN_NAME='SERIALIZED_WEIGHT_BOXES';
 if n=0 then
  execute immediate 'alter table RRL_SKU_RECEIPT_POLICY add SERIALIZED_WEIGHT_BOXES number(1)default 0 not null';
  execute immediate 'alter table RRL_SKU_RECEIPT_POLICY add constraint RRL_SKU_WEIGHT_BOX_FLAG_C check(SERIALIZED_WEIGHT_BOXES in(0,1))';
 end if;
end;
/
