declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SKU_RULE' and COLUMN_NAME='ALLOW_PICK_BATCH_MIX';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_SKU_RULE add(ALLOW_PICK_BATCH_MIX number(1) default 0 not null check(ALLOW_PICK_BATCH_MIX in(0,1)))';end if;
end;
/
